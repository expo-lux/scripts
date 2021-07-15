import os
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep
import traceback

from asterisk.ami import Action, AMIClient

#глобальная переменная, хранит результат звонка
test_result = ''
#сервер Asterisk
host = os.environ['ASTER_HOST']  # Asterisk with AMI and test dialplan
#логин AMI
user = os.environ['AMI_LOGIN']  # AMI user
password = os.environ['AMI_PASS']  # AMI password


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        try:
            s = self.path
            d = urllib.parse.parse_qs(s[2:])
            self._set_headers()
            number = d['number'][0]
            if 'trunk' in d:
                trunk = d['trunk'][0]
            else:
                trunk = ''
            self.wfile.write(self._html(number + ' ' + trunk))
            res = 1
            count = 0
            while(res):
                res = call(number, trunk)
                print('call result {}'.format(res))
                sleep(10)
                count += 1
                # выходим из цикла в случае успешного дозвона или если не смогли дозвониться в течение n=3 попыток
                if count >= 3:
                    break
        except Exception as e:
            s = traceback.format_exc()
            self.send_error(400)

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write(self._html("POST!"))


def run(server_class=HTTPServer, handler_class=S, addr="0.0.0.0", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()


def done(future):
    global test_result
    if future.status == 'Error':
        test_result = 'ERROR'

#функция в которой анализируем события приходящие из Asterisk
#dialplan, по которому делаем вызов, должен генерировать события UserEvent, например
#[call-file]
#exten => s,n,UserEvent(EVENT_OK,Start event)
def event_notification(source, event):
    global test_result
    keys = event.keys
    if 'UserEvent' in keys:
        if keys['UserEvent'] == 'EVENT_IVR':
            print('EVENT_ENTER_IVR')
        if keys['UserEvent'] == 'EVENT_WRONGANSWER':
            print('EVENT_WRONG_ANSWER')
        if keys['UserEvent'] == 'EVENT_OK':
            print('OK')
            test_result = 'OK'
        if keys['UserEvent'] == 'EVENT_TOOMUCH':
            print('EVENT_TOOMUCH')
            test_result = 'INVALID_ANSWER'
        if keys['UserEvent'] == 'EVENT_TIMEOUT':
            print('EVENT_TIMEOUT')
            test_result = 'TIMEOUT'


def call(number, trunk):
    global test_result
    test_result = ''
    context = {
        "context": "call-file",
        "extension": "s",
        "priority": 1
    }
    # call_to = 'SIP/242'  тестовый вызов
    # вызываемый номер в формате SIP/номер@транк
    if trunk:
        call_to = 'SIP/' + number + '@' + trunk
    else:
        call_to = 'SIP/' + number
    # получаем только пользовательские события
    aEnableEvents = Action('Events', keys={'EventMask': 'user'})

    # originate вызов и необходимые параметры (context, channel, extension, priority, CID)
    aOriginateCall = Action('Originate',
                            keys={'Channel': call_to, 'Context': context['context'], 'Exten': context['extension'],
                                  'Priority': context['priority'], 'CallerId': '999'}
                            )
    # Init AMI client and try to login
    client = AMIClient(host)

    #на данном этапе прослушиватель будет получать все события
    client.add_event_listener(event_notification)

    try:
        future = client.login(user, password)
        # This will wait for 1 second or fail
        if future.response.is_error():
            raise Exception(str(future.response.keys['Message']))
    except Exception as e:
        client.logoff()
        s = traceback.format_exc()
        test_result = 'ERROR'
        #sys.exit('Error: {}'.format(s))

    print('Spawned AMI session to: {}'.format(host))
    print('Logged in as {}'.format(user))

    try:
        #устанавливаем фильтр на получаемые события
        client.send_action(aEnableEvents, None)
        #Action: Originate, т.е. совершаем звонок
        client.send_action(aOriginateCall, done)
        print('Originated call to {}'.format(call_to))

    except Exception as e:
        client.logoff()
        s = traceback.format_exc()
        test_result = 'ERROR'
        #sys.exit('Error: {}'.format(s))

    print('Waiting for events...')

    # Wait for events during timelimit interval
    for i in range(70):
        time.sleep(1)
        # If test_result is changed (via events), then stop waiting
        if test_result:
            break;
    else:
        client.logoff()
        test_result ='TIMEOUT'
        #sys.exit('Error: time limit exceeded')
    client.logoff()
    codes = {
        'OK': 0,
        'TIMEOUT': 1,
        'ERROR': 2,
        'INVALID_ANSWER': 3,
    }
    return codes[test_result]


if __name__ == "__main__":
    run()