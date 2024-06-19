import json
import requests
from google.cloud import storage
import random
import datetime
import bb

def get_db(w):
    single_digits = [1,2,3,4,5,6,7,8,9]
    if w in single_digits:
        week_string = '0' + str(w)
    else:
        week_string = str(w)
    transactions = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/transactions/' + 'week_' + week_string + '/transactions.json').download_as_string())
    return transactions

def get_api(w):
    transactions_url = bb.config.url_pre['transaction'] + bb.config.current_league_id + bb.config.url_suf['transaction'] + str(w)
    transactions = json.loads(requests.get(transactions_url).text)
    return transactions
    
def preview_db(w):
    transactions = get_db(w)
    single_digits = [1,2,3,4,5,6,7,8,9]
    if w in single_digits:
        week_string = '0' + str(w)
    else:
        week_string = str(w)
    print("-------------------------------------")
    print('PREVIEWING TRANSACTIONS DB FILE FOR ' + bb.config.current_league_year + ' WEEK: ' + week_string)
    print("-------------------------------------")
    print('TYPE: LIST OF DICT WITH KEYS:')
    print(transactions[0].keys())
    print("-------------------------------------")
    print('SAMPLE RECORD:')
    for index,value in enumerate(transactions):
        if index < 1:
            print(json.dumps(value,indent=4))
    print("-------------------------------------")

def preview_api(w):
    transactions = get_api(w)
    print("-------------------------------------")
    print('PREVIEWING TRANSACTIONS API RESULT FOR ' + bb.config.current_league_year + ' WEEK: ' + str(w))
    print("-------------------------------------")
    print('TYPE: LIST OF DICT WITH KEYS:')
    print(transactions[0].keys())
    print("-------------------------------------")
    print('SAMPLE RECORD:')
    for index,value in enumerate(transactions):
        if index < 1:
            print(json.dumps(value,indent=4))
    print("-------------------------------------")

def update_db():
    lg_fetch = []
    for i in bb.config.league_info.keys():
        if bb.config.league_info[i]['archived'] == False:
            print('transactions - ' + bb.config.league_info[i]['year'] + ': league is not archived, fetching data')
            lg_fetch.append(i)
        else:
            print('transactions - ' + bb.config.league_info[i]['year'] + ': league is archived, using archived data')
    for i in lg_fetch:
        year = bb.config.league_info[i]['year']
        weeks = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
        for w in weeks:
            transactions_url = bb.config.url_pre['transaction'] + i + bb.config.url_suf['transaction'] + str(w)
            transactions = json.loads(requests.get(transactions_url).text)
            with open('transactions.json','w') as f:
                json.dump(transactions,f,indent=4)
                f.close()
                fp = 'resources/data/'
                fn = 'transactions.json'
                single_digits = [1,2,3,4,5,6,7,8,9]
                if w in single_digits:
                    week_string = '0' + str(w)
                else:
                    week_string = str(w)
                ul = bb.config.bucket.blob(fp + year + '/transactions/' + 'week_' + week_string + '/' + fn)
                ul.cache_control = 'no-store'
                ul.upload_from_filename(fn)
