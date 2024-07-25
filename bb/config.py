import requests
import json
import json
import requests
from google.cloud import storage
import random
import datetime

current_league_year = '2023'
next_league_year = '2024'
storage_client = storage.Client('bourbon-bowl')
bucket = storage_client.bucket('www.bourbon-bowl.com') # prod
# bucket = storage_client.bucket('dev-www.bourbon-bowl.com') # dev

league_info = json.loads(requests.get('https://raw.githubusercontent.com/bourbonbowl/bb/main/_league_info.json').text)

current_league_id = ''
for k,v in league_info.items():
    if v['year'] == current_league_year:
        current_league_id = k

url_pre = json.loads(requests.get('https://raw.githubusercontent.com/bourbonbowl/bb/main/_url_prefix.json').text)

url_suf = json.loads(requests.get('https://raw.githubusercontent.com/bourbonbowl/bb/main/_url_suffix.json').text)