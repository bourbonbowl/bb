import json
import requests
from google.cloud import storage
import random
import datetime
import bb
import pandas

def go():
    bb_summary_output = bb._compile.bb_summary_output()
    random_entry = {
        'Team':'RANDOM TEAM - ' + str(datetime.datetime.now()),
        'Player':'RANDOM PLAYER - ' + str(datetime.datetime.now()),
        'Position':'FB',
        'Draft Value':random.randint(10000, 60000),
        'End Of Season Value':random.randint(10000, 60000),
        'Keeper Value':random.randint(10000, 60000)
        }
    # bb_summary_output.append(random_entry)
    bb_summary_output_df = pandas.DataFrame(bb_summary_output)
    
    with open('bb_summary_output.json','w') as f:
        json.dump(bb_summary_output,f,indent=4)
        f.close()
        fp = 'resources/data/'
        fn = 'bb_summary_output.json'
        ul = bb.config.bucket.blob(fp + fn)
        ul.cache_control = 'no-store'
        ul.upload_from_filename(fn)
        print('data posted to: ' + fp + fn)
            
    with open('bb_summary_output.csv','w') as f:
        bb_summary_output_df.to_csv(f,header=True,index=False)
        f.close()
        fp = 'resources/data/'
        fn = 'bb_summary_output.csv'
        ul = bb.config.bucket.blob(fp + fn)
        ul.cache_control = 'no-store'
        ul.upload_from_filename(fn)
        print('data posted to: ' + fp + fn)
    
    faab_flow = bb._compile.faab_flow()
    faab_flow_result = faab_flow.to_json(orient="records")
    faab_flow_parsed = json.loads(faab_flow_result)
    
    with open('faab_flow.json','w') as f:
        json.dump(faab_flow_parsed,f,indent=4)
        f.close()
        fp = 'resources/data/'
        fn = 'faab_flow.json'
        ul = bb.config.bucket.blob(fp + fn)
        ul.cache_control = 'no-store'
        ul.upload_from_filename(fn)
        print('data posted to: ' + fp + fn)
            
    with open('faab_flow.csv','w') as f:
        faab_flow.to_csv(f,header=True,index=False)
        f.close()
        fp = 'resources/data/'
        fn = 'faab_flow.csv'
        ul = bb.config.bucket.blob(fp + fn)
        ul.cache_control = 'no-store'
        ul.upload_from_filename(fn)
        print('data posted to: ' + fp + fn)