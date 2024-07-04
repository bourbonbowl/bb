import json
import requests
from google.cloud import storage
import random
import datetime
import pandas
import numpy
import bb

players = json.loads(requests.get(bb.config.url_pre['player'] + bb.config.url_suf['player']).text)

def lookupTeam(user_id):
    users = bb.users.get_db()
    for i in users:
        if i['user_id'] == str(user_id):
            try:
                return i['metadata']['team_name']
            except:
                return i['display_name']

def lookupPlayer(id):
    player_detail = str(players[str(id)]['first_name']) + ' ' + str(players[str(id)]['last_name']) + ' - ' + str(players[str(id)]['team']) + ' - ' + str(players[str(id)]['position'])
    return player_detail

def start():
    waiver_log = []
    weeks = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
    for week in weeks:
        if week in [1,2,3,4,5,6,7,8,9]:
            transactions = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/transactions/week_0' + str(week) + '/transactions.json').download_as_string())
        else:
            transactions = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/transactions/week_' + str(week) + '/transactions.json').download_as_string())
        for i in transactions:
            if i['type']=='waiver' and i['metadata']['notes']!='Unfortunately, your roster will have too many players after this transaction.':
                entry = {
                    'week':week,
                    'transaction_id':i['transaction_id'],
                    'player_id':str(list(i['adds'].keys())[0]),
                    'status_updated':i['status_updated'],
                    'team':i['creator'],
                    'bid':i['settings']['waiver_bid'],
                    'status':i['status']
                    # ,'notes':i['metadata']['notes']
                }
                waiver_log.append(entry)
    return waiver_log


def compile():
    waiver_log = start()
    # create base dataframe
    df_waiver_log = pandas.DataFrame(waiver_log)
    df_waiver_log = df_waiver_log.sort_values(['status_updated','player_id'])
    df_waivers_complete = df_waiver_log[df_waiver_log['status'] == 'complete']
    # create df: waivers_failed
    df_waivers_failed = df_waiver_log[df_waiver_log['status'] == 'failed']
    # create df: waivers_summary
    # time, player, total teams bidding
    df_waivers_summary = df_waiver_log.groupby(['week','status_updated','player_id'])['team'].nunique()
    df_waivers_summary = df_waivers_summary
    df_waivers_summary = df_waivers_summary.reset_index()
    # create df: waivers_complete_summary
    # time, player, winner, winner bid
    df_waivers_complete_summary = df_waivers_complete[['week','status_updated', 'player_id', 'team', 'bid']].copy().reset_index()
    df_waivers_complete_summary = df_waivers_complete_summary.drop(columns=['index'])
    df_waivers_complete_summary = df_waivers_complete_summary.rename({'team': 'team_win', 'bid': 'bid_win'}, axis='columns')
    # create df: waivers_failed_summary
    # time, player, max bidder, max bidder bid
    df_waivers_failed_summary = df_waivers_failed.copy()
    df_waivers_failed_summary['bid_rank'] = df_waivers_failed_summary.groupby(['week','status_updated','player_id'])['bid'].rank(method='dense',ascending=False)
    df_waivers_failed_summary['team_name'] = df_waivers_failed_summary['team'].apply(lookupTeam)
    df_waivers_failed_summary = df_waivers_failed_summary.groupby(['week','status_updated','player_id','bid','bid_rank'])['team_name'].apply(lambda x : ' / '.join(x)).reset_index(name='teams_runnerup')
    df_waivers_failed_summary = df_waivers_failed_summary[df_waivers_failed_summary['bid_rank'] == 1]
    df_waivers_failed_summary = df_waivers_failed_summary.drop(columns=['bid_rank'])
    df_waivers_failed_summary = df_waivers_failed_summary.rename({'bid': 'bid_runnerup', 'teams_runnerup': 'team_runnerup'}, axis='columns')
    # create merged df
    df_waivers = df_waivers_summary.merge(df_waivers_complete_summary, how='left', on=['week','status_updated', 'player_id'])
    df_waivers = df_waivers.merge(df_waivers_failed_summary, how='left', on=['week','status_updated', 'player_id'])
    df_waivers = df_waivers[df_waivers['team_win'].notna()]
    df_waivers['bid_runnerup'] = df_waivers['bid_runnerup'].fillna(0)
    df_waivers['team_runnerup'] = df_waivers['team_runnerup'].fillna('-')
    # delta winnng bid and runner up bid
    df_waivers['bid_delta'] = df_waivers['bid_win'] - df_waivers['bid_runnerup']
    # lone ranger flag
    df_waivers['flag_lr'] = numpy.where((df_waivers['team'] == 1), 'Lone Ranger', '')
    # free parking flag
    df_waivers['flag_fp'] = numpy.where((df_waivers['team'] > 1) & (df_waivers['bid_win'] == 0), 'Free Parking', '')
    # on target flag
    df_waivers['flag_ot'] = numpy.where((df_waivers['bid_win'] > 1) & (df_waivers['bid_delta'] <= 1), 'On Target', '')
    # overpay flag
    df_waivers['flag_op'] = numpy.where((df_waivers['bid_delta'] > 1) & (df_waivers['bid_delta'] < 10), 'Overpay', '')
    # malpractice flag
    df_waivers['flag_mp'] = numpy.where((df_waivers['bid_delta'] > 10), 'Malpractice', '')
    # sweepstakes flag
    df_waivers['flag_ss'] = numpy.where((df_waivers['team'] >= 6), 'Sweepstakes', '')
    #combine flags
    # step 1
    df_waivers['flags'] = df_waivers['flag_lr'] + '/' + df_waivers['flag_fp']
    df_waivers['flags'] = df_waivers['flags'].str.replace('^\/','',regex=True)
    df_waivers['flags'] = df_waivers['flags'].str.replace('\/$','',regex=True)
    # step 2
    df_waivers['flags'] = df_waivers['flags'] + '/' + df_waivers['flag_ot']
    df_waivers['flags'] = df_waivers['flags'].str.replace('^\/','',regex=True)
    df_waivers['flags'] = df_waivers['flags'].str.replace('\/$','',regex=True)
    # step 3
    df_waivers['flags'] = df_waivers['flags'] + '/' + df_waivers['flag_op']
    df_waivers['flags'] = df_waivers['flags'].str.replace('^\/','',regex=True)
    df_waivers['flags'] = df_waivers['flags'].str.replace('\/$','',regex=True)
    # step 4
    df_waivers['flags'] = df_waivers['flags'] + '/' + df_waivers['flag_mp']
    df_waivers['flags'] = df_waivers['flags'].str.replace('^\/','',regex=True)
    df_waivers['flags'] = df_waivers['flags'].str.replace('\/$','',regex=True)
    # step 5
    df_waivers['flags'] = df_waivers['flags'] + '/' + df_waivers['flag_ss']
    df_waivers['flags'] = df_waivers['flags'].str.replace('^\/','',regex=True)
    df_waivers['flags'] = df_waivers['flags'].str.replace('\/$','',regex=True)
    # get player info
    df_waivers['player'] = df_waivers['player_id'].apply(lookupPlayer)
    # get team info
    df_waivers['team_win'] = df_waivers['team_win'].apply(lookupTeam)
    # create output df
    df_output = df_waivers[['week','player','team_win','flags','team_runnerup', 'bid_win','bid_runnerup','bid_delta']].copy().reset_index()
    df_output = df_output.drop(columns=['index'])
    return df_output