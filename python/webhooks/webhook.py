import logging, time, sys, json, re
import yaml
import traceback
import smtplib
import html
import bottle
from bottle import get, post, request, response

from email.header import Header
from email.mime.text import MIMEText

@get('/')
def do_get():
    logger.info("GET request,\nPath: %s\n", str(request.path))

@post('/')
def do_post():
    try:
        #request.json возвращает объект только если в заголовке указан content-type: application/json
        #нижеописанная конструкция вернет объект независимо от заголовка(хотя мб это и неправильно)
        s = request.body.read()
        data = json.loads(s)
        logger.info("POST request,\nPath: %s\nBody:\n%s\n",
                    str(request.path), json.dumps(data, indent=2, ensure_ascii=False))

        processed = get_messages(data)
        result = json.dumps(processed, ensure_ascii=False)
        logger.debug("Response:\n %s", json.dumps(processed, indent=2, ensure_ascii=False))
        response.content_type = 'application/json'
        response.body = result
        response.status = 200

        for item in processed:
            send_mail(config['smtp_subject'], config['smtp_from'], item['recipients'], item['message'])

    except Exception as e:
        response.status = 400
        s = traceback.format_exc()
        logger.error(s)

    finally:
        return response


def get_module_logger(mod_name, loglevel=logging.DEBUG):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    tz = time.strftime('%z')
    f = '|%(asctime)s' + tz + '|%(levelname)s|%(name)s|%(message)s'
    formatter = logging.Formatter(fmt=f)
    formatter.default_msec_format = '%s.%03d'
    handler.setFormatter(formatter)
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(handler)
    logger.setLevel(loglevel)
    return logger


def filter_items(items, whitelist, blacklist):
    """
    """
    whitelist_regex = []
    blacklist_regex = []
    filtered_items = []
    for raw_regex in whitelist:
        whitelist_regex.append(re.compile(raw_regex))
    for raw_regex in blacklist:
        blacklist_regex.append(re.compile(raw_regex))
    for item in items:
        if any(reg.search(item) for reg in whitelist_regex):
            if not any(reg.search(item) for reg in blacklist_regex):
                logger.debug("Item %s is in whitelist and not in blacklist" % item)
                filtered_items.append(item)
    return filtered_items


def process_rule(items, rule):
    """
    """
    whitelist = rule['whitelist']
    blacklist = rule['blacklist']
    return filter_items(items, whitelist, blacklist)


def process_request(request):
    """
    """
    result = []
    rules = config.get('create_rules', [])
    for rule in rules:
        item = {}
        logger.debug('Process added files')
        files = request['modifications']['added']
        item['recipients'] = rule['e-mail']
        item['message_template'] = rule['message_template']
        item['files'] = process_rule(files, rule)
        if item['files']:
            result.append(item)

    rules = config.get('update_rules', [])
    for rule in rules:
        item = {}
        logger.debug('Process modified files')
        files = request['modifications']['modified']
        item['recipients'] = rule['e-mail']
        item['message_template'] = rule['message_template']
        item['files'] = process_rule(files, rule)
        if item['files']:
            result.append(item)

    rules = config.get('delete_rules', [])
    for rule in rules:
        item = {}
        logger.debug('Process removed files')
        files = request['modifications']['removed']
        item['recipients'] = rule['e-mail']
        item['message_template'] = rule['message_template']
        item['files'] = process_rule(files, rule)
        if item['files']:
            result.append(item)
    return result


def send_mail(subject: str, sender: str, recipients: list, message: str):
    """
    """
    if recipients :
        targets = ', '.join(recipients)

        logger.info('Send message to %s' % targets)
        logger.debug('Subject: %s' % subject)
        logger.debug('Sender: %s' % sender)
        logger.debug('Recipients: %s' % targets)
        logger.debug('Message: %s' % message)

        msg = MIMEText(message)
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = sender
        msg['To'] = targets

        server = smtplib.SMTP("%s:%d" % (config['smtp_server'], config['smtp_port']))
        server.starttls()
        server.login(config['smtp_username'], config['smtp_password'])
        server.sendmail(config['smtp_username'], recipients, msg.as_string())
        server.quit()


def get_messages(request):
    """
    """
    processed = []
    x = {}
    author_mail = request['author']['mail']
    author_name = html.unescape(
        request['author']['name'])  # Замена numeric character reference notation в юникод-строку
    description = html.unescape(request['description'])
    id = request['id']
    result = process_request(request)
    for item in result:
        x['recipients'] = [s.format(author_mail=author_mail) for s in item['recipients']]
        files = ''.join(s + '\n' for s in item['files'])
        x['message'] = item['message_template'].format(author_mail=author_mail,
                                                       author_name=author_name, description=description, id=id,
                                                       files=files)
        processed.append(x.copy())
    return processed


def read_request_from_file(filename):
    """
    """
    try:
        file = open(filename, 'r', encoding='utf-8')
        request = json.load(file)
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    finally:
        file.close()
    return request


def read_config(filename='config.yml'):
    """
    """
    temp_log = get_module_logger("read_config")
    try:
        file = open(filename, 'r', encoding='utf-8')
        conf = yaml.safe_load(file)
    except Exception as e:
        temp_log.error(e)
        temp_log.error("Can't read config file " + filename)
        temp_log.error("Exiting")
        sys.exit(1)
    finally:
        file.close()

    loglevel = conf['loglevel']

    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        temp_log.error("Invalid loglevel: " + loglevel)
        sys.exit(1)
    else:
        conf['loglevel'] = numeric_level

    return conf

if __name__ == '__main__':
    config = read_config()
    logger = get_module_logger("main", config['loglevel'])
    logger.info("Webhook started")

    from sys import argv

    if len(argv) == 2:
        bottle.run(host='0.0.0.0', port=int(argv[1]), debug=False, quiet=True)
    else:
        bottle.run(host='0.0.0.0', port=9998)
