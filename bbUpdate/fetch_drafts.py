import json
import requests
from google.cloud import storage
import random
import datetime
import bbUpdate

def go():
    draft_fetch = []
    lg_fetch = []
    for i in bbUpdate.config.league_info.keys():
        if bbUpdate.config.league_info[i]['archived'] == False:
            print('draft - ' + bbUpdate.config.league_info[i]['year'] + ': league is not archived, fetching data')
            lg_fetch.append(i)
            draft_fetch.append(bbUpdate.config.league_info[i]['draft_id'])
        else:
            print('draft - ' + bbUpdate.config.league_info[i]['year'] + ': league is archived, using archived data')
        for i in draft_fetch:
            for key, item in bbUpdate.config.league_info.items():
                if item['draft_id'] == i:
                    # print(item['draft_id'])
                    lg_id = key
                    year = bbUpdate.config.league_info[lg_id]['year']
                    # print(yr)
                    draft_url = bbUpdate.config.url_pre['draft'] + i + bbUpdate.config.url_suf['draft']
                    drafts = json.loads(requests.get(draft_url).text)
                    with open('drafts.json','w') as f:
                        json.dump(drafts,f,indent=4)
                        f.close()
                        fp = 'resources/data/'
                        fn = 'drafts.json'
                        ul = bbUpdate.config.bucket.blob(fp + year + '/drafts/' + fn)
                        ul.cache_control = 'no-store'
                        ul.upload_from_filename(fn)

def get_db():
    drafts = json.loads(bbUpdate.config.bucket.blob('resources/data/' + bbUpdate.config.current_league_year + '/drafts/drafts.json').download_as_string())
    return drafts

def get_api():
    drafts_url = bbUpdate.config.url_pre['draft'] + bbUpdate.config.league_info[bbUpdate.config.current_league_id]['draft_id'] + bbUpdate.config.url_suf['draft']
    drafts = json.loads(requests.get(drafts_url).text)
    return drafts

def preview_db():
    drafts = get_db()
    print('previewing current drafts db file')
    for index,value in enumerate(drafts):
        if index < 3:
            print(json.dumps(value,indent=4))

def preview_api():
    drafts = get_api()
    print('previewing current drafts via api')
    for index,value in enumerate(drafts):
        if index < 3:
            print(json.dumps(value,indent=4))