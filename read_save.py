import pyodbc
import pandas as pd

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-LOQ5BTR;'
                      'Database=kinan;'
                      'Trusted_Connection=yes;')


def keys_and_values(dictanory):
    values = ''
    if isinstance(dictanory, list):
        keylist = dictanory[0]
        for item in dictanory:
            placeholders = ''
            for value in item.values():
                placeholders = placeholders + ', ' + ('\'' + str(value) + '\'')
            placeholders = placeholders[2:]
            values = values + ' ,(' + placeholders + ')'
        values = values[2:]

    else:
        placeholders = ''
        keylist = dictanory
        for value in dictanory.values():
            placeholders = placeholders + ', ' + ('\'' + str(value) + '\'')
        values = '(' + placeholders[2:] + ')'

    columns = ''
    for key in keylist.keys():
        #         key=key.replace('-','_')
        columns = columns + ', ' + str(key)
    columns = columns[2:]
    return columns, values


def update_item_in_database(db, item, con):
    cursor = conn.cursor()
    sql = ''
    for key in item.keys():
        sql = sql + ', %s =\'%s\'' % (key, item[key])
    sql = 'update %s set %s where %s' % (db, sql[1:], con)
    #     print (sql)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    del cursor


def save_to_database(db, columns, values):
    cursor = conn.cursor()
    sql = "INSERT INTO %s ( %s ) VALUES  %s  " % (db, columns, values)
    # print(sql)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    del cursor


def read_from_database(db, condition, indicator='*', extra=''):
    sql = 'select %s from %s where %s %s' % (indicator, db, condition, extra)
    cursor = conn.cursor()
    # print(sql)
    crs = cursor.execute(sql)
    if crs.rowcount == 0:
        return 'null'
    rawdata = crs.fetchall()
    if len(rawdata) == 1:
        i = 0
        data = {}
        column_names = [col[0] for col in cursor.description]
        for column in column_names:
            data[column] = rawdata[0][i]
            i += 1
        return data
    desc = cursor.description
    column_names = [col[0] for col in desc]
    data = [dict(zip(column_names, row)) for row in rawdata]
    return data


# ---------------------------MATCHSTATS---------------------------------------------------------
def get_matchstats(gameId, server, puuid='*'):
    conditions = 'gameId = %s and platformId = \'%s\' ' % (gameId, server)
    matchstats = read_from_database('matchstats', conditions)
    if matchstats == 'null':
        return matchstats, matchstats, matchstats
    teams = read_from_database('teams', conditions)
    conditions = 'gameId = %s and platformId = \'%s\' ' % (gameId, server.upper())
    if puuid == '*':
        participants = read_from_database('participants', conditions, extra='order by participantId')
        return matchstats, teams, participants
    participants = read_from_database('participants', conditions + 'and puuid = \'%s\'' % puuid)
    return matchstats, teams, participants


def save_matchstats(matchstats, teams, participants):
    columns, values = keys_and_values(matchstats)
    save_to_database('matchstats', columns, values)
    columns, values = keys_and_values(teams)
    save_to_database('teams', columns, values)
    participants = pd.DataFrame(participants)
    participants.drop(participants[participants['accountId'] == '0'].index, inplace=True)
    participants.fillna(0, inplace=True)
    participants = participants.astype({'perkSubStyle': int, 'perkPrimaryStyle': int})
    participants = participants.to_dict('records')
    columns, values = keys_and_values(participants)
    save_to_database('participants', columns, values)


# ---------------------------MATCHLIST--------------------------------------------------------
def save_matchlist(matchlist):
    for match in matchlist['matches']:
        match['puuid'] = matchlist['puuid']
    columns, values = keys_and_values(matchlist['matches'])
    save_to_database('matchlist', columns, values)


def get_matchlist(puuid, con=''):
    if con != '': con = 'and' + con
    condition = 'puuid = \'%s\' %s' % (puuid, con)
    matchlist = read_from_database('matchlist', condition, extra='order by timestamp desc')
    return matchlist


# ---------------------------SUMMONER----------------------------------------------------------
def save_summoner(summoner):
    summoner['name'] = (summoner['name'].lower()).replace(' ', '')
    columns, values = keys_and_values(summoner)
    save_to_database('summoner', columns, values)


def update_summoner(summoner):
    summoner['name'] = (summoner['name'].lower()).replace(' ', '')
    condition = 'puuid = \'' + summoner['puuid'] + '\''
    update_item_in_database('summoner', summoner, condition)


def get_summoner(puuid):
    summoner = read_from_database('summoner', 'puuid = \'%s\'' % puuid)
    return summoner


def get_summoner_by_name(name, server):
    name = (name.lower()).replace(' ', '')
    summoner = read_from_database('summoner', 'name = \'%s\' and platformId = \'%s\'' % (name, server))
    return summoner


# ---------------------------TIMELINE---------------------------------------------------------
# -----------------------------RANK-----------------------------------------------------------
def get_rank(puuid, cons=''):
    if cons != '': cons = 'and' + cons
    rank = read_from_database('summoner', 'puuid =\'%s\'' % puuid + cons)
    return rank


def save_rank(rank):
    columns, values = keys_and_values(rank)
    save_to_database('rank', columns, values)


def update_rank(rank):
    for queue in rank:
        condition = 'puuid = \'%s\' and queueType = \'%s\'' % (rank['puuid'], rank['queuetype'])
        update_item_in_database('rank', queue, condition)


# ---------------------------MASTERY----------------------------------------------------------
def all_summoners():
    puuid = 'euw1'
    summoner = read_from_database('summoner', 'platformId = \'%s\'' % puuid, indicator='name')
    return summoner
