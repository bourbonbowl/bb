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
    current_week = int(datetime.datetime.today().strftime("%V"))
    if current_week not in [36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,1,2]:
        users = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.next_league_year + '/users.json').download_as_string())
    else:
        users = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/users.json').download_as_string())
    return users

def get_api():
    '''
    function loads and returns data from the api
    '''
    users = json.loads(requests.get(bb.config.url_pre['user'] + bb.config.current_league_id + bb.config.url_suf['user']).text)
    return users

def preview_db():
    ''' 
    function loads and returns a preview of the db data
    '''
    users = get_db()
    print("-------------------------------------")
    print('PREVIEWING USERS DB FILE')
    print("-------------------------------------")
    print('TYPE: LIST OF DICT WITH KEYS:')
    print(users[0].keys())
    print("-------------------------------------")
    print('SAMPLE RECORD:')
    for index,value in enumerate(users):
        if index < 1:
            print(json.dumps(value,indent=4))
    print("-------------------------------------")

def preview_api():
    ''' 
    function loads and returns a preview of the api data
    '''
    users = get_api()
    print("-------------------------------------")
    print('PREVIEWING USERS API RESULT')
    print("-------------------------------------")
    print('TYPE: LIST OF DICT WITH KEYS:')
    print(users[0].keys())
    print("-------------------------------------")
    print('SAMPLE RECORD:')
    for index,value in enumerate(users):
        if index < 1:
            print(json.dumps(value,indent=4))
    print("-------------------------------------")


def update_db():
    '''
    function updates the db data
    '''
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

def lookupTeam(user_id):
    '''
    function takes user_id and returns team name
    '''
    users = bb.users.get_db()
    for i in users:
            if i['user_id'] == str(user_id):
                try:
                    return i['metadata']['team_name']
                except:
                    return i['display_name']