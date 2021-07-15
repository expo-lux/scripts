import os
import requests

# r = requests.get('https://api.vk.com/method/ads.getStatistics?v=5.92&account_id=1605052472&ids_type=ad&'
#     'ids=50556193&'
#     'access_token=f18c2c60535df5395e3a53fa8c8cb1a2a42af15fd2534574277c5e6fc5d86f5a9ef7f586b215d74a2f9a3&'
#     'period=day&date_from=0&date_to=2019-02-10')


r = requests.get('https://api.vk.com/method/ads.getStatistics?v=5.92&account_id=1605052472&ids_type=ad&'
    'ids=50556193&'
    'access_token=f18c2c60535df5395e3a53fa8c8cb1a2a42af15fd2534574277c5e6fc5d86f5a9ef7f586b215d74a2f9a3&'
    'period=day&date_from=0&date_to=0')

for i in r.json()['response']:
    dir = os.getcwd() + '\\' + str(i['id'])
    filename = str(i['id']) + '.json'
    outfile = dir + '\\' + filename
    s = ''
    if (not os.path.isdir(dir)):
        os.mkdir(dir)
    for k in i['stats']:
        k['ad'] = str(i['id'])
        s = s + str(k) + '\n'
    f = open(outfile,'w')
    s = s.replace("'", '"')
    print(s)

    f.write(s)
