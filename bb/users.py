import json
import requests
from google.cloud import storage
import random
import datetime
import bb

def get_db():
    users = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/users.json').download_as_string())
    return users

def get_api():
    users = json.loads(requests.get(bb.config.url_pre['user'] + bb.config.current_league_id + bb.config.url_suf['user']).text)
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
    for i in bb.config.league_info.keys():
        if bb.config.league_info[i]['archived'] == False:
            print('users - ' + bb.config.league_info[i]['year'] + ': league is not archived, fetching data')
            lg_fetch.append(i)
        else:
            print('users - ' + bb.config.league_info[i]['year'] + ': league is archived, using archived data')
    for i in lg_fetch:
        year = bb.config.league_info[i]['year']
        users = json.loads(requests.get(bb.config.url_pre['user'] + bb.config.current_league_id + bb.config.url_suf['user']).text)
        with open('users.json','w') as f:
            json.dump(users,f,indent=4)
            f.close()
            fp = 'resources/data/'
            fn = 'users.json'
            ul = bb.config.bucket.blob(fp + year + '/' + fn)
            ul.cache_control = 'no-store'
            ul.upload_from_filename(fn)