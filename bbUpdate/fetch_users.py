import json
import requests
from google.cloud import storage
import random
import datetime
import bbUpdate

def go():
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