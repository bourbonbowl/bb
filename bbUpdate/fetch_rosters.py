import json
import requests
from google.cloud import storage
import random
import datetime
import bbUpdate

def go():
    roster_fetch = []
    for i in bbUpdate.config.league_info.keys():
        if bbUpdate.config.league_info[i]['archived'] == False:
            print('roster - ' + bbUpdate.config.league_info[i]['year'] + ': league is not archived, fetching data')
            roster_fetch.append(i)
        else:
            print('roster - ' + bbUpdate.config.league_info[i]['year'] + ': league is archived, using archived data')
    for i in roster_fetch:
        year = bbUpdate.config.league_info[i]['year']
        roster_url = bbUpdate.config.url_pre['roster'] + i + bbUpdate.config.url_suf['roster']
        rosters = json.loads(requests.get(roster_url).text)
        with open('rosters.json','w') as f:
            json.dump(rosters,f,indent=4)
            f.close()
            fp = 'resources/data/'
            fn = 'rosters.json'
            ul = bbUpdate.config.bucket.blob(fp + year + '/' + fn)
            ul.cache_control = 'no-store'
            ul.upload_from_filename(fn)