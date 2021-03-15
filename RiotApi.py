import RiotConsts as Consts
from requests.exceptions import HTTPError
import time
import requests
import sys

esc = ['esc', 'back', 'exit']


class RiotApi(object):
    def __init__(self, *, api_key=Consts.API_KEY, region="europe_west"):
        self.api_key = api_key
        while True:
            if region in Consts.REGIONS.keys():
                self.region = Consts.REGIONS[region]
                break
            elif region in Consts.REGIONS.values():
                self.region = region
                break
            elif region in esc:
                sys.exit()
            else:
                print("""
    please enter a supported region
    supported regions :
        europe_nordic_and_east : eun1
        europe_west : euw1
        brazil : br1
        japan : jp
        korea : kr
        latin_america_north : la1
        latin_america_south : la2
        north_america : na1
        oceania :  oc1
        turkey : tr1
        russia : ru""")
                region = input('please enter your region :')
        self.params = ''

    def _requests(self, api_url, params=None):
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        response = requests.get(
            Consts.URL["base"].format(
                region=self.region,
                url=api_url,
                api_key=self.api_key,
                params=self.params
            ),
            params
        )
        # print(response.url)  # testfunction
        response.raise_for_status()
        # test
        # end test
        return response.json()

    def summoner_by_id(self, summonerid):
        api_url = Consts.URL['summoner_by_id'].format(
            version=Consts.API_VERSION['summoner'],
            summoner_id=summonerid
        )
        return self.server_overload(api_url)

    def summoner_by_name(self, name):
        api_url = Consts.URL["summoner_by_name"].format(
            version=Consts.API_VERSION['summoner'],
            summoner_name=name
        )
        return self.server_overload(api_url)

    def summoner_by_puuid(self, puuid):
        api_url = Consts.URL["summoner_by_puuid"].format(
            version=Consts.API_VERSION['summoner'],
            puuid=puuid
        )
        return self.server_overload(api_url)

    def summoner_by_account(self, accountid):
        api_url = Consts.URL["summoner_by_account"].format(
            version=Consts.API_VERSION['summoner'],
            accountid=accountid
        )
        return self.server_overload(api_url)

    def get_matchlist(self, summoner_id, champion='', queue='', season='', begin_time='', begin_index=''):
        api_url = Consts.URL["matches_by_summoner_id"].format(
            version=Consts.API_VERSION['match'],
            summoner_id=summoner_id
        )
        matchlist_params = {}
        if champion:
            matchlist_params["champion"] = champion
        if queue:
            matchlist_params["queue"] = queue
        if season:
            matchlist_params["season"] = season
        if begin_time:
            matchlist_params["beginTime"] = begin_time
        if begin_index:
            matchlist_params['beginIndex'] = begin_index
        # print(matchlist_params)
        return self._requests(api_url, matchlist_params)

    def get_matchstats(self, match_id):
        api_url = Consts.URL['match_info'].format(
            version=Consts.API_VERSION['match'],
            match_id=match_id
        )
        return self.server_overload(api_url)

    def get_timeline(self, match_id):
        api_url = Consts.URL['match_timeline'].format(
            version=Consts.API_VERSION['match'],
            match_id=match_id
        )
        return self._requests(api_url)

    def champion_mastery(self, summoner_id, champion_id):
        api_url = Consts.URL['champion_mastery'].format(
            version=Consts.API_VERSION['mastery'],
            summoner_id=summoner_id,
            champion_id=champion_id
        )
        return self.server_overload(api_url)

    def live_game(self, summoner_id):
        api_url = Consts.URL['live_game'].format(
            version=Consts.API_VERSION['spectator'],
            summoner_id=summoner_id
        )
        return self.server_overload(api_url)

    def summoner_rank(self, summonerId):
        api_url = Consts.URL['rank'].format(
            version=Consts.API_VERSION['rank'],
            encryptedSummonerId=summonerId
        )
        return self.server_overload(api_url)

    def server_overload(self, api_url):
        while True:
            try:
                return self._requests(api_url)
            except HTTPError as e:
                if e.response.status_code in (429, 504, 503):
                    # print(e.response.status_code)
                    time.sleep(5)
                    continue
                else:
                    return self._requests(api_url)
