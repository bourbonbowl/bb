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