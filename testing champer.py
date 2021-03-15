from RiotApi import RiotApi
from IPython.display import display
import bs4
from tqdm import tqdm

api = RiotApi()
import RiotConsts
import preparedata
import getdata
import read_save as rs
import pandas as pd
from IPython.display import display_html
import os
import webbrowser
import preparehtml
import userinput

getdata.define_api()


def collect_all_data(summoners):
    pbar = tqdm(summoners, bar_format='livegame:'
                                      '{l_bar}{bar}|')
    i = 0
    for summoner in pbar:
        print(summoner)
        if i > 402:
            sucsses, matchlist = getdata.get_matchlist(summoner['name'])
            if sucsses:
                getdata.get_matchstats_from_matchlist(matchlist)
                # result = analyize.predict(participants)
                # # print(result)
                # summoner.update(result)
                # summoners.append(summoner)
                # print(summoner)
            else:
                print(matchlist)
        i = i + 1


summoners = rs.all_summoners()
print(summoners)
collect_all_data(summoners)
