import json
import requests
from google.cloud import storage
import random
import datetime
import bb

def get_db():
    drafts = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/drafts/drafts.json').download_as_string())
    return drafts

def get_api():
    drafts_url = bb.config.url_pre['draft'] + bb.config.league_info[bb.config.current_league_id]['draft_id'] + bb.config.url_suf['draft']
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

def update_db():
    draft_fetch = []
    lg_fetch = []
    for i in bb.config.league_info.keys():
        if bb.config.league_info[i]['archived'] == False:
            print('draft - ' + bb.config.league_info[i]['year'] + ': league is not archived, fetching data')
            lg_fetch.append(i)
            draft_fetch.append(bb.config.league_info[i]['draft_id'])
        else:
            print('draft - ' + bb.config.league_info[i]['year'] + ': league is archived, using archived data')
        for i in draft_fetch:
            for key, item in bb.config.league_info.items():
                if item['draft_id'] == i:
                    # print(item['draft_id'])
                    lg_id = key
                    year = bb.config.league_info[lg_id]['year']
                    # print(yr)
                    draft_url = bb.config.url_pre['draft'] + i + bb.config.url_suf['draft']
                    drafts = json.loads(requests.get(draft_url).text)
                    with open('drafts.json','w') as f:
                        json.dump(drafts,f,indent=4)
                        f.close()
                        fp = 'resources/data/'
                        fn = 'drafts.json'
                        ul = bb.config.bucket.blob(fp + year + '/drafts/' + fn)
                        ul.cache_control = 'no-store'
                        ul.upload_from_filename(fn)