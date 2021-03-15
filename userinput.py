import preparehtml
import getdata
import time
import data_analyize as analyize
from tqdm import tqdm

esc = ['esc', 'back', 'exit']


def get_input():
    user_input = input('''what do you want to do:
    1. search a (game) 
    2. search a (summoner)
    3. analyize  a (live game)''')
    if user_input in esc: getdata.define_api()
    input_parameters = input('''enter gameId or summoner name
enter esc or back if you want to choose something else''')
    input_handling(user_input, input_parameters)


def input_handling(user_input, input_parameters):
    if input_parameters in esc: get_input()
    if user_input == '1' or user_input == 'game' or user_input == 'search a game':
        game_handling(input_parameters)
    if user_input == '2' or user_input == 'summoner' or user_input == 'search summoner':
        summoner_handling(input_parameters)
    if user_input == '3' or user_input == 'live game' or user_input == 'analyize live game':
        live_game(input_parameters)
    get_input()


def game_handling(input_parameters):
    if input_parameters in esc: get_input()
    if input_parameters.isdigit():
        match, teams, participants = getdata.get_matchstats(input_parameters)
        if match:
            preparehtml.prepare_game(match, teams, participants)
            get_input()
        else:
            print(teams)
            input_parameters = input()
            game_handling(input_parameters)
    else:
        input_parameters = input('''sorry there is no game with this Id
        please make sure of the game Id''')
        game_handling(input_parameters)


def summoner_handling(input_parameters):
    if input_parameters in esc: get_input()
    sucsses, summoner = getdata.get_summoner(input_parameters)
    if sucsses:
        sucsses, match_list = getdata.get_matchlist(summoner['name'])
        if sucsses:
            # for match in match_list:
            # match['timestamp']=match['timestamp']
            preparehtml.prepare_summoner_page(summoner, match_list)
        else:
            print(match_list)
            get_input()
    else:
        print(summoner)
        input_parameters = input('please enter the summoner name again and make sure if you are on the right server')
        summoner_handling(input_parameters)


def live_game(input_paramaters):
    if input_paramaters in esc: get_input()
    sucsses, summoner = getdata.get_summoner(input_paramaters)
    if sucsses:
        live_game_opreation(summoner)
    else:
        print(summoner)
        input_paramaters = input('please enter the summoner name again and make sure if you are on the right server')
        live_game(input_paramaters)


def live_game_opreation(summoner):
    start = time.time()
    sucsses, game = getdata.get_live_game(summoner['summonerId'])
    if sucsses:
        summoners = []
        pbar = tqdm(game['participants'], bar_format='livegame:'
                                                     '{l_bar}{bar}|')

        for summoner in pbar:
            sucsses, matchlist = getdata.get_matchlist(summoner['summonerName'])
            if sucsses:
                games, teams, participants = getdata.get_matchstats_from_matchlist(matchlist)
                result = analyize.predict(participants)
                # print(result)
                summoner.update(result)
                summoners.append(summoner)
                # print(summoner)
            else:
                print(matchlist)
                get_input()
    else:
        print(game)
        get_input()
    end = time.time()
    # print('it took', end - start, 'sec to finish live game procces')
    preparehtml.prepare_livegame_page(summoners)
