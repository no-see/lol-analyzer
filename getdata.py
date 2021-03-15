from RiotApi import RiotApi
import read_save as rs
# api = RiotApi()
import preparedata as pd
from requests.exceptions import HTTPError
import time
from tqdm import tqdm


def define_api():
    global api
    region = input('please enter your region:')
    api = RiotApi(region=region)


def check_summoner(name):
    summoner = rs.get_summoner_by_name(name, api.region)
    if summoner =='null' :
        return get_summoner(name)
    else :
        return True,summoner

def get_summoner_by_accountid(accountid):
    try:
        summoner = api.summoner_by_account(accountid)
    except HTTPError as e:
        if e.response.status_code == 404:
            error = 'summoner not found , please enter summoner name correctly'
            return False, error
        elif e.response.status_code == 403:
            error = 'sorry it seams our server are having an issue please wait '
            print('error 403 has occurd try to update the api key')
            return False, error
        error = 'something went wrong'
        return False, error
    summoner = pd.prepare_summoner(summoner, api.region)
    # check if the summoner is in the database by puuid
    # if the summoner was in the database update it

    newsummoner = rs.get_summoner(summoner['puuid'])
    if not newsummoner == 'null':
        rs.update_summoner(summoner)
        if newsummoner['lastcache'] != 666: summoner['lastcache'] = newsummoner['lastcache']
    else:
        rs.save_summoner(summoner)

def get_summoner(accountindicator):
    try:
        if len(accountindicator) < 60:
            summoner = api.summoner_by_name(accountindicator)

        else:
            summoner = api.summoner_by_puuid(accountindicator)

    except HTTPError as e:
        if e.response.status_code == 404:
            error = 'summoner not found , please enter summoner name correctly'
            return False, error
        elif e.response.status_code == 403:
            error = 'sorry it seams our server are having an issue please wait '
            print('error 403 has occurd try to update the api key')
            return False, error
        error = 'something went wrong'
        return False, error
    summoner = pd.prepare_summoner(summoner, api.region)
    # check if the summoner is in the database by puuid
    # if the summoner was in the database update it

    newsummoner = rs.get_summoner(summoner['puuid'])
    if not newsummoner == 'null':
        rs.update_summoner(summoner)
        if newsummoner['lastcache'] != 666: summoner['lastcache'] = newsummoner['lastcache']
    else:
        rs.save_summoner(summoner)

    return True, summoner


def get_matchlist(summonername):
    date = (int(round(time.time() * 1000)) - 432000000)
    sucsses, summoner = get_summoner(summonername)
    if not sucsses: return (False, summoner)
    if 'lastcache' in summoner:
        saved_matchlist = rs.get_matchlist(summoner['puuid'], ' timestamp > '+str(date))
        date = summoner['lastcache']
    else:
        saved_matchlist = rs.get_matchlist(summoner['puuid'])
    try:
        full_matchlist = api.get_matchlist(summoner['accountId'], begin_time=date)
    except HTTPError as e:
        if e.response.status_code == 404:
            print('there is no new games')
            matchlist = saved_matchlist
            if matchlist == 'null':
                return (False, 'this player didn\'t play since 30 days')
            #             print(e)
            return (True, matchlist)
        print(e)
        if not (e.response.status_code in (429, 504, 503)):
            return (False, 'somthing wrong happend sit tight while we are working to solve it')
        else :
            soso = 4
    total_games = full_matchlist['totalGames']
    total_games -= 100
    i = 0

    while (int(total_games) - 1) > 0:
        i = i + 100  # I =begain index
        partial_matchlist = api.get_matchlist(summoner['accountId'], begin_time=date, begin_index=i)
        full_matchlist['matches'] = full_matchlist['matches'] + partial_matchlist['matches']
        total_games -= 100

    #     full_matchlist['matches'] = full_matchlist['matches']+matchlist['matches']
    # start of saving matchlist
    summoner['lastcache'] = full_matchlist['matches'][0]['timestamp'] + 100
    rs.update_summoner(summoner)
    full_matchlist['puuid'] = summoner['puuid']
    rs.save_matchlist(full_matchlist)
    # end saving matchlist
    if saved_matchlist != 'null': full_matchlist['matches'] = full_matchlist['matches'] + saved_matchlist
    return (True, full_matchlist['matches'])


def get_matchstats(matchId):
    match, teams, participants = rs.get_matchstats(matchId, api.region)
    if not match == 'null':
        return (match, teams, participants)
    try:
        match = api.get_matchstats(matchId)
    except HTTPError as e:
        if e.response.status_code == 404:
            return (False, '''
                sorry there is no game with this Id
                please make sure of the game Id
                ''', '')
        if e.response.status_code in [429, 504, 503]:
            so=1
    match, teams, participants = pd.prepare_matchstats(match)
    if not match:
        return (False,False,False)
    #     for participant in participants : get_summoner(participant['puuid'])
    rs.save_matchstats(match, teams, participants)
    return (match, teams, participants)


def get_live_game(summonerId):
    try:
        live_game = api.live_game(summonerId)
    except HTTPError as e:
        if e.response.status_code == 404:
            return False, "the player is not in a game right now"
        else:
            return False, "sorry something seems wrong please try again later"
    return True, live_game

# def get_timline(matchId):
def get_matchstats_from_matchlist(matchlist):
    gameId = []
    games = []
    teams = []
    participants=[]
    for match in matchlist:
        gameId.append(match['gameId'])
    gameId = tqdm(gameId,bar_format='suumoner:'
                                    '{l_bar}{bar}')
    for Id in gameId:
        game,team,participant = get_matchstats(Id)
        games.append(game)
        teams = team +teams
        for item in participant:
            item['gamelength'] = game['gameDuration']
        participants = participants+participant
    return games,teams,participants