import json
import requests
from google.cloud import storage
import random
import datetime
import bbUpdate

def go():
	players = json.loads(requests.get(bbUpdate.config.url_pre['player'] + bbUpdate.config.url_suf['player']).text)
	with open('players.json','w') as f:
		json.dump(players,f,indent=4)
		f.close()
		fp = 'resources/data/'
		fn = 'players.json'
		ul = bbUpdate.config.bucket.blob(fp + fn)
		ul.cache_control = 'no-store'
		ul.upload_from_filename(fn)
