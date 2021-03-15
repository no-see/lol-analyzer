import os
import webbrowser
import pandas as pd
import bs4
import RiotConsts

wcd = 'file:///' + 'D:/projects/lol api project alpha/'


def display_html(html):
    path = os.path.abspath('D:/projects/lol api project alpha/temp.html')
    url = 'file://' + path

    with open(path, 'w') as f:
        f.write(str(html))
    webbrowser.open(url)


# ==================================GAME PREPARING=========================================================


def prepare_game(game, teams, participants):
    items = ['6', '7', '8', '9', '10', '11', '12']
    teams = pd.DataFrame(teams)
    participants = pd.DataFrame(participants)
    participants = participants.rename(
        columns={'championId': 'champion', 'spell1Id': 'spell1', 'spell2Id': 'spell2', 'summonerName': 'name'})
    # print(participants)
    participants = participants.drop(
        ['platformId', 'gameId', 'summonerId', 'participantId', 'teamId', 'accountId', 'currentPlatformId',
         'currentAccountId', 'matchHistoryUri', 'combatPlayerScore', 'sightWardsBoughtInGame',
         'objectivePlayerScore', 'totalPlayerScore', 'totalScoreRank', 'playerScore0', 'playerScore1', 'playerScore2',
         'playerScore3', 'playerScore4', 'playerScore5', 'playerScore6', 'playerScore7', 'playerScore8',
         'playerScore9', ], axis=1)
    game = pd.DataFrame([game])
    html = participants.style.render()
    html = bs4.BeautifulSoup(html,features="html.parser")
    index = participants.index
    number_of_rows = len(index)
    rows = html.table.find('tbody').find_all('tr')

    for k in range(number_of_rows):
        for i in items:
            html = replace_with_image(html, k, i, 'item')
        html = replace_with_image(html, k, 0, 'champion')
        html = replace_with_image(html, k, 1, 'spell')
        html = replace_with_image(html, k, 2, 'spell')
        html = replace_with_image(html, k, 4, 'profileicon')
        win = html.find('td', 'data row%s col%s' % (k, 5))
        if win.string == 'True':
            win['style'] = 'color:#00ff00 ;'
        elif win.string == 'False':
            win['style'] = 'color:red;'
    k = 0
    for row in rows:
        if k <= 4:
            row['style'] = 'background-color:#4d97f0;'
        else:
            row['style'] = 'background-color:#f86565;'
        k = k + 1
    display_html(html)


# ====================================SUMMONER HANDLING=============================================
def prepare_summoner_page(summoner, matchlist):
    matchlist = pd.DataFrame(matchlist)
    # matchlist['timestamp'] = pd.to_datetime(matchlist['timestamp'], unit='D')
    matchlist['timestamp'] = pd.to_datetime(matchlist['timestamp'],unit='ms')
    matchlist['timestamp'] = matchlist['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    matchlist = matchlist.drop(['puuid'], axis=1)
    index = matchlist.index
    with open('D:/projects/lol api project alpha/'+'index.html', 'r') as f:
        html = f.read()
    matchlist = matchlist.style.render()
    matchlist = bs4.BeautifulSoup(matchlist,features="html.parser")
    number_of_rows = len(index)
    for k in range(number_of_rows):
        matchlist = replace_with_image(matchlist, k, 3, 'champion')
    html = bs4.BeautifulSoup(html,features="html.parser")
    html.find('img', id="i6q5b")['src'] = wcd + RiotConsts.DRAGON + 'img\\profileicon\\' + str(
        summoner['profileIconId']) + '.png'
    html.find('div', id='i3kef').string = 'level :' + str(summoner['summonerLevel'])
    html.find('div', id="in8zk").string = summoner['shownname']
    pointer = html.find('hr')
    pointer.insert_after(matchlist.table)
    display_html(html)


# ==================================LIVE GAME=========================================================
def prepare_livegame_page(summoners):
    participants = pd.DataFrame(summoners)
    participants = participants.rename(
        columns={'championId': 'champion', 'spell1Id': 'spell1', 'spell2Id': 'spell2', 'summonerName': 'name',
                 'visonary': 'vision'})
    # print(participants, participants.shape)
    participants = participants.drop(['summonerId', 'gameCustomizationObjects', 'perks', 'teamId'], axis=1)
    participants[['vision', 'turretdestroyer', 'split', 'survivor']] = participants[
        ['vision', 'turretdestroyer', 'split', 'survivor']].astype(int)
    html = participants.style.render()
    html = bs4.BeautifulSoup(html,features="html.parser")
    # display_html(html)
    index = participants.index
    number_of_rows = len(index)
    rows = html.table.find('tbody').find_all('tr')
    for k in range(number_of_rows):
        html = replace_with_image(html, k, 2, 'champion')
        html = replace_with_image(html, k, 0, 'spell')
        html = replace_with_image(html, k, 1, 'spell')
        html = replace_with_image(html, k, 3, 'profileicon')
        html = replace_labels(html, k, 6)
        html = replace_labels(html, k, 7)
        html = replace_labels(html, k, 8)
        html = replace_labels(html, k, 9)

    k = 0
    for row in rows:
        if k <= 4:
            row['style'] = 'background-color:#4d97f0;'
        else:
            row['style'] = 'background-color:#f86565;'
        k = k + 1
    display_html(html)


# ===================================EXTRA FUNCTIONS===============================================
def find_image(kind, imgId):
    path = wcd + RiotConsts.DRAGON + 'img\\%s\\' % kind + imgId + '.png'
    if kind == 'champion' or kind == 'profileicon':
        image = bs4.BeautifulSoup().new_tag('img', style='display:block', width='60px', hieght='100%', src=path)
    else:
        image = bs4.BeautifulSoup().new_tag('img', width='45px', hieght='45px', src=path)
    return image


def replace_with_image(html, row, col, kind):
    item = html.table.find('td', 'data row%s col%s' % (row, col))
    if item.string == '0':
        item.string = ''
        return html
    if kind == 'champion':
        image = find_image(kind, RiotConsts.CHAMPION[item.string])
    elif kind == 'spell':
        image = find_image(kind, RiotConsts.SUMMONER[item.string])
    else:
        image = find_image(kind, item.string)
    item.string = ''
    item.insert(0, image)
    return html


def replace_labels(html, row, col):
    item = html.table.find('td', 'data row%s col%s' % (row, col))
    if item.string == '0':
        item.string = ''
        return html
    if col == 6:
        if item.string == '1':
            item.string = 'visionary'
            item['style'] = 'background-color:#089b08;'
        else:
            item.string = 'bad vision'
            item['style'] = 'background-color:#fa2727;'
        return html
    elif col == 9:
        if item.string == '1':
            item.string = 'survivor'
            item['style'] = 'background-color:#089b08;'
        else:
            item.string = 'vulnerable'
            item['style'] = 'background-color:#fa2727;'
        return html
    else:
        item['style'] = 'background-color:#edd735;'
        item.string = "true"
        return html
