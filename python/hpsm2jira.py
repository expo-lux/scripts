import imaplib
import email
import sys
import logging
import traceback
import re
from bs4 import BeautifulSoup
from jira import JIRA


# получить идентификатор задачи из темы письма
def getHPSMIdFromSubject(subject):
    pattern = re.compile('(IM|C|T)\d{8}')
    res = pattern.search(subject)
    if res:
        return res.group()

def fetchFirstEmail(mail):
    status, data = mail.fetch(b'1', '(RFC822)')
    msg_raw = data[0][1]
    return email.message_from_bytes(msg_raw, _class=email.message.EmailMessage)

def moveFirstEmailToArchive(mail):
    result = mail.copy(b'1', 'Archive')
    if result[0] == 'OK':
        mov, data = mail.store(b'1', '+FLAGS', '(\Deleted)')
        mail.expunge()
    return result[0]

def taskExistsInJira(jira, taskname):
    query = 'summary ~ ' + taskname + ' AND project = pimi-2 and reporter = hpsm2jira'
    issues = jira.search_issues(query)
    return len(issues) > 0

def searchOpenTaskInJira(jira, taskname):
    query = 'summary ~ ' + taskname + ' AND project = pimi-2 and reporter = hpsm2jira and resolution = Unresolved'
    issues = jira.search_issues(query)
    return len(issues) > 0

def getEmailCharset(msg):
    sub = email.header.decode_header(msg["Subject"])
    return sub[0][1]

def getEmailSubject(msg):
    charset = getEmailCharset(msg)
    sub = email.header.decode_header(msg["Subject"])
    return sub[0][0].decode(charset)

def getEmailBody(msg):
    charset = getEmailCharset(msg)
    body = msg.get_payload(decode=True).decode(charset)
    soup = BeautifulSoup(body, 'html.parser')
    s = soup.prettify()
    soup2 = BeautifulSoup(s, 'html.parser')
    s = soup2.get_text()
    return s.replace('\n\n', '\n').replace('  \n', '')

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='processing.log')
# logging.getLogger("requests").setLevel(logging.WARNING)

logger = logging.getLogger('hpsm2jira')
logger.setLevel(logging.DEBUG)

project_name = 'pimi2'
issue_type = 'Routine'
mailbox_username = 'hpsm2jira@x.ru'
mailbox_pass = 'pass'
try:
    logger.info('Connecting to http://jira.x.ru with login  hpsm2jira')
    jac = JIRA('http://jira.x.ru', basic_auth=('hpsm2jira', 'pass'), logging=False)
    logger.info('Connected')
    logger.info('Connecting to ' + mailbox_username)
    mail = imaplib.IMAP4_SSL('imap.yandex.ru')
    mail.login(mailbox_username, mailbox_pass)
    logger.info('Connected')
except Exception as e:
    logger.error(traceback.format_exc())
    sys.exit(1)

# работа с уведомлениями о назначении задач
folder = "Backlog"
result, numMessages = mail.select(folder)
if result != 'OK':
    logger.error('Cannot select %s folder', folder)
    sys.exit(1)

result, data = mail.search(None, 'ALL')
num = len(data[0].split())
count = int(numMessages[0])
if count != num:
    logger.error('Ошибка. Количество сообщений не совпадает')
    sys.exit(1)
logger.info('Selecting %s folder, founded %d messages', folder, count)
i = 0
while i < count:
    try:
        msg = fetchFirstEmail(mail)
        subject = getEmailSubject(msg)
        logger.info('  ' + subject)

        if msg.is_multipart():
            raise Exception('    Multipart e-mail. Skip processing')

        HPSMId = getHPSMIdFromSubject(subject)
        if not HPSMId:
            raise Exception('    HPSM ID not found in subject')
        logger.info('    Found ' + HPSMId + ' in subject of the email')

        if taskExistsInJira(jac, HPSMId):
            raise Exception('    Issue with such HPSM ID is always present in JIRA')

        description = getEmailBody(msg)
        issue_dict = dict(project={'key': project_name}, summary=subject, description=description,
                          issuetype={'name': issue_type})
        new_issue = jac.create_issue(fields=issue_dict)
        logger.info('    Create issue %s %s in project %s', issue_type, new_issue.key, project_name)

    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        logger.info('    Move message to archive folder')
        moveFirstEmailToArchive(mail)
        i = i + 1

# работа с уведомлениями о решении задач и закрытие задач в jira
# fetch mail only from Resolved folder. This folder must contain only emails for closed tasks.
# What emails should go to this folder depends on email processing rules.
folder = "Resolved"
result, numMessages = mail.select(folder)
if result != 'OK':
    logger.error('Cannot select %s folder', folder)
    sys.exit(1)
count = int(numMessages[0])
logger.info('Selecting %s folder, founded %d messages', folder, count)
i = 0
HPSMId = None
while i < count:
    try:
        msg = fetchFirstEmail(mail)
        subject = getEmailSubject(msg)
        logger.info('  ' + subject)

        if msg.is_multipart():
            raise Exception('    Multipart e-mail. Skip processing')

        HPSMId = getHPSMIdFromSubject(subject)
        if not HPSMId:
            raise Exception('    HPSM ID not found in subject')
        logger.info('    Found ' + HPSMId + ' in subject of the email')

        if not searchOpenTaskInJira(jac, HPSMId):
            raise Exception('    Cannot found open issue in JIRA with HPSM ID = ' + HPSMId + '. Nothing to resolve')

        query = 'summary ~ ' + HPSMId + ' AND project = pimi-2 and reporter = hpsm2jira and resolution = Unresolved'
        issues = jac.search_issues(query)
        if len(issues) > 1:
            raise Exception('    Found more than one open issue with HPSM ID = ' + HPSMId )

        # transitions = jac.transitions(issues[0])
        # transition to 'done' id='21'
        rslt = jac.transition_issue(issues[0], '21')
        logger.info('    Transition ' + issues[0].fields.summary + ' to Done')

    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        logger.info('    Move message to archive folder')
        moveFirstEmailToArchive(mail)
        i = i + 1

mail.close()
mail.logout()
logger.info('Close mailbox')
