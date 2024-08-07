import json
import requests
from google.cloud import storage
import random
import datetime
import bb

def get_db():
    '''
    function loads and returns data from the db
    '''
    rosters = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/rosters.json').download_as_string())
    return rosters

def get_api():
    '''
    function loads and returns data from the api
    '''
    rosters = json.loads(requests.get(bb.config.url_pre['roster'] + bb.config.current_league_id + bb.config.url_suf['roster']).text)
    return rosters

def preview_db():
    ''' 
    function loads and returns a preview of the db data
    '''
    rosters = get_db()
    print("-------------------------------------")
    print('PREVIEWING ROSTERS DB FILE')
    print("-------------------------------------")
    print('TYPE: LIST OF DICT WITH KEYS:')
    print(rosters[1].keys())
    print("-------------------------------------")
    print('SAMPLE RECORD:')
    for index,value in enumerate(rosters):
        if index < 1:
            print(json.dumps(value,indent=4))
    print("-------------------------------------")

def preview_api():
    ''' 
    function loads and returns a preview of the api data
    '''
    rosters = get_api()
    print("-------------------------------------")
    print('PREVIEWING ROSTERS API RESULT')
    print("-------------------------------------")
    print('TYPE: LIST OF DICT WITH KEYS:')
    print(rosters[1].keys())
    print("-------------------------------------")
    print('SAMPLE RECORD:')
    for index,value in enumerate(rosters):
        if index < 1:
            print(json.dumps(value,indent=4))
    print("-------------------------------------")
        
def update_db():
    '''
    function updates the db data
    '''
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