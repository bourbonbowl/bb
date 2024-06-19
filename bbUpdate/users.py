import json
import requests
from google.cloud import storage
import random
import datetime
import bbUpdate

def get_db():
    users = json.loads(bbUpdate.config.bucket.blob('resources/data/' + bbUpdate.config.current_league_year + '/users.json').download_as_string())
    return users

def get_api():
    users = json.loads(requests.get(bbUpdate.config.url_pre['user'] + bbUpdate.config.current_league_id + bbUpdate.config.url_suf['user']).text)
    return users

def preview_db():
    users = get_db()
    print('previewing current users db file')
    for index,value in enumerate(users):
        if index < 15:
            print(json.dumps(value['display_name'],indent=4))

def preview_api():
    users = get_api()
    print('previewing current users via api')
    for index,value in enumerate(users):
        if index < 15:
            print(json.dumps(value['display_name'],indent=4))

def update_db():
    lg_fetch = []
    for i in bbUpdate.config.league_info.keys():
        if bbUpdate.config.league_info[i]['archived'] == False:
            print('users - ' + bbUpdate.config.league_info[i]['year'] + ': league is not archived, fetching data')
            lg_fetch.append(i)
        else:
            print('users - ' + bbUpdate.config.league_info[i]['year'] + ': league is archived, using archived data')
    for i in lg_fetch:
        year = bbUpdate.config.league_info[i]['year']
        users = json.loads(requests.get(bbUpdate.config.url_pre['user'] + bbUpdate.config.current_league_id + bbUpdate.config.url_suf['user']).text)
        with open('users.json','w') as f:
            json.dump(users,f,indent=4)
            f.close()
            fp = 'resources/data/'
            fn = 'users.json'
            ul = bbUpdate.config.bucket.blob(fp + year + '/' + fn)
            ul.cache_control = 'no-store'
            ul.upload_from_filename(fn)