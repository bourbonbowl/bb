import json
import requests
from google.cloud import storage
import random
import datetime
import bb

def get_db():
    rosters = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/rosters.json').download_as_string())
    return rosters

def get_api():
    rosters = json.loads(requests.get(bb.config.url_pre['roster'] + bb.config.current_league_id + bb.config.url_suf['roster']).text)
    return rosters

def preview_db():
    rosters = get_db()
    print('previewing current rosters db file')
    for index,value in enumerate(rosters):
        if index < 1:
            print(json.dumps(value,indent=4))

def preview_api():
    rosters = get_api()
    print('previewing current users via api')
    for index,value in enumerate(rosters):
        if index < 1:
            print(json.dumps(value,indent=4))
        
def update_db():
    roster_fetch = []
    for i in bb.config.league_info.keys():
        if bb.config.league_info[i]['archived'] == False:
            print('roster - ' + bb.config.league_info[i]['year'] + ': league is not archived, fetching data')
            roster_fetch.append(i)
        else:
            print('roster - ' + bb.config.league_info[i]['year'] + ': league is archived, using archived data')
    for i in roster_fetch:
        year = bb.config.league_info[i]['year']
        roster_url = bb.config.url_pre['roster'] + i + bb.config.url_suf['roster']
        rosters = json.loads(requests.get(roster_url).text)
        with open('rosters.json','w') as f:
            json.dump(rosters,f,indent=4)
            f.close()
            fp = 'resources/data/'
            fn = 'rosters.json'
            ul = bb.config.bucket.blob(fp + year + '/' + fn)
            ul.cache_control = 'no-store'
            ul.upload_from_filename(fn)