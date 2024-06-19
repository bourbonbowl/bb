import json
import requests
from google.cloud import storage
import random
import datetime
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
            if i['type']=='waiver' and i['status']=='complete':
                for key in i['adds']:
                    if key not in bb_completed_waivers:
                        bb_completed_waivers[key] = {}
                        bb_completed_waivers[key].update({i['status_updated']:i['settings']['waiver_bid']})
            
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