import json
import requests
from google.cloud import storage
import random
import datetime
import bbUpdate

def go():
    bb_summary_output = bbUpdate.data_compile.go()
    random_entry = {
            'Team':'RANDOM TEAM - ' + str(datetime.datetime.now()),
            'Player':'RANDOM PLAYER - ' + str(datetime.datetime.now()),
            'Position':'FB',
            'Draft Value':random.randint(10000, 60000),
            'End Of Season Value':random.randint(10000, 60000),
            'Keeper Value':random.randint(10000, 60000)
            }
    # bb_summary_output.append(random_entry)
    with open('bb_summary_output.json','w') as f:
            json.dump(bb_summary_output,f,indent=4)
            f.close()
            fp = 'resources/data/'
            fn = 'bb_summary_output.json'
            ul = bbUpdate.config.bucket.blob(fp + fn)
            ul.cache_control = 'no-store'
            ul.upload_from_filename(fn)
            print('data posted to: ' + fp + fn)