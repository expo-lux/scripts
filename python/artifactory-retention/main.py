import json
import requests, argparse
from datetime import datetime


def clean_artifactory_repo(base_url, apikey, aql_text, dry_run=True, start_gc=False):
    headers = {
        'content-type': 'text/plain',
        'X-JFrog-Art-Api': apikey
    }

    only_key = {
        'X-JFrog-Art-Api': apikey
    }

    js = json.dumps(aql_text)
    js = js.replace("\"$eq\": 0", "\"$eq\": null")
    # print(js)
    data = 'items.find(' + js + ').sort({"$desc" : ["created"]})'
    myResp = requests.post(base_url + 'api/search/aql', headers=headers, data=data)

    d = datetime.now()
    evaluated = json.loads(myResp.text)
    count = evaluated["range"]["total"]
    print("{} Found {} artifacts".format(d, count))
    print("First 2 artifacts will be skipped")
    items = evaluated["results"]
    isDockerRepo = False
    if len(items) > 2:
        repo = items[0]['repo']
        result = requests.get(base_url + 'api/repositories/' + repo, headers=only_key)
        isDockerRepo = json.loads(result.text)['packageType'] == 'docker'
        iter_items = iter(items)
        #skip 2 first artifacts
        next(iter_items)
        next(iter_items)
        for result in iter_items:
            if isDockerRepo:
                artifact_url = base_url + result['repo'] + '/' + result['path']
            else:
                artifact_url = base_url + result['repo'] + '/' + result['path'] + '/' + result['name']
            print(artifact_url)
            print(result)
            if not dry_run:
                requests.delete(artifact_url, headers=headers)
        if not dry_run:
            # empty thrash can
            res = requests.post(base_url + 'api/trash/empty', headers=headers)
            if start_gc:
                # run garbage collection
                res = requests.post(base_url + 'api/system/storage/gc', headers=headers)


if __name__ == '__main__':

    d = datetime.now()
    try:
        file = open("config.json", 'r', encoding='utf-8')
        conf = json.load(file)
    except Exception as e:
        print(e)
        print("Can't read config file config.json")
        print("Exiting")
        sys.exit(1)
    finally:
        file.close()

    parser = argparse.ArgumentParser(description='artifactory-retention')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--start-gc", action="store_true")
    args = parser.parse_args()

    clean_artifactory_repo(conf["baseurl"], conf["apikey"], conf["filter"], args.dry_run, args.start_gc)