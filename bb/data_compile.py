import json
import requests
from google.cloud import storage
import random
import datetime
import pandas
import numpy
import bb


def go():
    # get players
    players = json.loads(bb.config.bucket.blob('resources/data/' + 'players.json').download_as_string())
    users = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/users.json').download_as_string())

    # compile user display name
    bb_users = {}
    for user in users:
        if "team_name" in user['metadata'].keys():
            bb_users.update({user['user_id']:user['metadata']['team_name']})
        else:
            bb_users.update({user['user_id']:user['display_name']})

    # compile rostered players
    roster = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/rosters.json').download_as_string())
    bb_rostered_players = {}
    for team in roster:
        for player in team['players']:
            entry = {'roster_id':team['roster_id']}
            bb_rostered_players[player] = entry

    # compile rosters
    bb_roster = {}
    for team in roster:
        entry = {'owner_id': team['owner_id']}
        bb_roster[team['roster_id']] = entry

    # compile draft
    draft = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/drafts/drafts.json').download_as_string())
    bb_draft = {}
    for selection in draft:
        entry = {'amount':selection['metadata']['amount'],'picked_by':selection['picked_by'],'is_keeper':selection['is_keeper']}
        bb_draft[selection['player_id']] = entry

    for k,v in bb_rostered_players.items():
        bb_rostered_players[k]['owner_id'] = bb_roster[v['roster_id']]['owner_id']

    # compile completed waivers
    bb_completed_waivers = {}
    weeks = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
    for week in weeks:
        if week in [1,2,3,4,5,6,7,8,9]:
            transactions = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/transactions/week_0' + str(week) + '/transactions.json').download_as_string())
        else:
            transactions = json.loads(bb.config.bucket.blob('resources/data/' + bb.config.current_league_year + '/transactions/week_' + str(week) + '/transactions.json').download_as_string())
        for i in transactions:
                for key in i['adds']:
                    if key not in bb_completed_waivers:
                        bb_completed_waivers[key] = {}
                        bb_completed_waivers[key].update({i['status_updated']:i['settings']['waiver_bid']})

    # compile transactions for FAABFlow
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
                    'transaction_id':i['transaction_id'],
                    'player_id':str(list(i['adds'].keys())[0]),
                    'status_updated':i['status_updated'],
                    'team':i['creator'],
                    'bid':i['settings']['waiver_bid'],
                    'status':i['status']
                    # ,'notes':i['metadata']['notes']
                }
                waiver_log.append(entry)
    # create base dataframe
    df_waiver_log = pandas.DataFrame(waiver_log)
    df_waiver_log = df_waiver_log.sort_values(['status_updated','player_id'])
    
    # create df: waivers_complete
    df_waivers_complete = df_waiver_log[df_waiver_log['status'] == 'complete']
    #print(df_waivers_complete.to_string())
    
    # create df: waivers_failed
    df_waivers_failed = df_waiver_log[df_waiver_log['status'] == 'failed']
    #print(df_waivers_failed.to_string())

    # create df: waivers_summary
    # time, player, total teams bidding
    df_waivers_summary = df_waiver_log.groupby(['status_updated','player_id'])['team'].nunique()
    df_waivers_summary = df_waivers_summary
    df_waivers_summary = df_waivers_summary.reset_index()
    
    # create df: waivers_complete_summary
    # time, player, winner, winner bid
    df_waivers_complete_summary = df_waivers_complete[['status_updated', 'player_id', 'team', 'bid']].copy().reset_index()
    df_waivers_complete_summary = df_waivers_complete_summary.drop(columns=['index'])
    df_waivers_complete_summary = df_waivers_complete_summary.rename({'team': 'team_win', 'bid': 'bid_win'}, axis='columns')

    # create df: waivers_failed_summary
    # time, player, max bidder, max bidder bid
    def lookupTeam(user_id):
     users = bb.users.get_db()
     for i in users:
             if i['user_id'] == str(user_id):
                     try:
                        return i['metadata']['team_name']
                     except:
                        return i['display_name']
    df_waivers_failed_summary = df_waivers_failed.copy()
    df_waivers_failed_summary['bid_rank'] = df_waivers_failed_summary.groupby(['status_updated','player_id'])['bid'].rank(method='dense',ascending=False)
    df_waivers_failed_summary['team_name'] = df_waivers_failed_summary['team'].apply(lookupTeam)
    df_waivers_failed_summary = df_waivers_failed_summary.groupby(['status_updated','player_id','bid','bid_rank'])['team_name'].apply(lambda x : ' / '.join(x)).reset_index(name='teams_runnerup')
    df_waivers_failed_summary = df_waivers_failed_summary[df_waivers_failed_summary['bid_rank'] == 1]
    df_waivers_failed_summary = df_waivers_failed_summary.drop(columns=['bid_rank'])
    df_waivers_failed_summary = df_waivers_failed_summary.rename({'bid': 'bid_runnerup', 'teams_runnerup': 'team_runnerup'}, axis='columns')
    # create merged df
    df_waivers = df_waivers_summary.merge(df_waivers_complete_summary, how='left', on=['status_updated', 'player_id'])
    df_waivers = df_waivers.merge(df_waivers_failed_summary, how='left', on=['status_updated', 'player_id'])
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
    # get player info
    # get team info
    # format date


    # create output df

    print(df_waiver_log.groupby(['status_updated','player_id'])['team'].nunique().to_string())
    print(df_waiver_log.groupby(['status_updated','player_id'])['bid'].nlargest(2).to_string())
    print(df_waiver_log.groupby(['status_updated','player_id'])['bid'].rank(method='dense').to_string())
    
                


    # compile most recent pickup
    bb_recent_waiver = {}
    for key, value in bb_completed_waivers.items():
        bb_recent_waiver[key] = value[max(value.keys())]

    # compile final value
    bb_rostered_players_final_value = {}
    for key in bb_rostered_players:
        if key in bb_draft.keys() and key not in bb_recent_waiver.keys():
            bb_rostered_players_final_value[key] = bb_draft[key]['amount']
        if key not in bb_draft.keys() and key in bb_recent_waiver.keys():
            bb_rostered_players_final_value[key] = bb_recent_waiver[key]
        if key in bb_draft.keys() and key in bb_recent_waiver.keys():
            bb_rostered_players_final_value[key] = bb_draft[key]['amount']
        if key not in bb_recent_waiver.keys() and key not in bb_draft.keys():
            bb_rostered_players_final_value[key] = 'ERROR'

    # compile keeper value
    bb_rostered_players_keeper_value = {}
    for key in bb_rostered_players_final_value:
        if int(bb_rostered_players_final_value[key]) > 35:
            keeper_value = round(int(bb_rostered_players_final_value[key]) * 1.15)
        elif int(bb_rostered_players_final_value[key]) == 0:
            keeper_value = 5
        else:
            keeper_value = round(int(bb_rostered_players_final_value[key]) + 5)
        bb_rostered_players_keeper_value[key] = keeper_value

    # compile league summary output
    bb_summary_output = []
    for key, value in bb_rostered_players.items():
        if players[key]['team'] is None:
            player_name = players[key]['full_name'] + ' - ' + 'NFL FA'
        else:
            player_name = players[key]['full_name'] + ' - ' + players[key]['team']
        if key in bb_draft.keys():
            draft_value = bb_draft[key]['amount']
        else:
            draft_value = 'Undrafted'
        entry = {
            'Team':bb_users[value['owner_id']],
            'Player':player_name,
            'Position':players[key]['position'],
            'Draft Value':draft_value,
            'End Of Season Value':bb_rostered_players_final_value[key],
            'Keeper Value':bb_rostered_players_keeper_value[key]
            }
        bb_summary_output.append(entry)
    return bb_summary_output

def preview():
    prev = go()
    for index,value in enumerate(prev):
        if index < 5:
            print(value)