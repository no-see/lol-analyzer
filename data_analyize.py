import csv
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

class_features = [
    ['kills', 'deaths', 'assists'],
    ['championId', 'visionWardsBoughtInGame', 'wardsPlaced', 'wardsKilled',
     'visionScore', 'gamelength', 'role'],
    ['damageDealtToObjectives', 'damageDealtToTurrets', 'turretKills',
     'inhibitorKills', ],
    ['kills', 'deaths', 'assists', 'totalDamageTaken', 'totalMinionsKilled', 'champLevel', 'turretKills',
     'damageDealtToTurrets']]
cleanup_roles_list = {'role': {'DUO_SUPPORT': 0, 'DUO': 1, 'SOLO': 2, 'DUO_CARRY': 3, 'NONE': 4},
                      'lane': {'TOP': 0, 'MIDDLE': 1, 'JUNGLE': 2, 'BOTTOM': 3, 'NONE': 4},
                      'win': {False: 0, True: 1},
                      'firstBloodKill': {False: 0, True: 1},
                      'firstBloodAssist': {False: 0, True: 1},
                      'firstTowerKill': {False: 0, True: 1},
                      'firstTowerAssist': {False: 0, True: 1},
                      'firstInhibitorKill': {False: 0, True: 1},
                      'firstInhibitorAssist': {False: 0, True: 1}
                      }
cleanup_roles = {'role': {'DUO_SUPPORT': 0, 'DUO': 1, 'SOLO': 2, 'DUO_CARRY': 3, 'NONE': 4},
                 'lane': {'TOP': 0, 'MIDDLE': 1, 'JUNGLE': 2, 'BOTTOM': 3, 'NONE': 4},
                 'win': {'False': 0, "True": 1},
                 'firstBloodKill': {'False': 0, "True": 1},
                 'firstBloodAssist': {'False': 0, "True": 1},
                 'firstTowerKill': {'False': 0, "True": 1},
                 'firstTowerAssist': {'False': 0, "True": 1},
                 'firstInhibitorKill': {'False': 0, "True": 1},
                 'firstInhibitorAssist': {'False': 0, "True": 1},
                 'visonary': {'-1': '2'},
                 'survivor': {'-1': '2'}
                 }
roles = ['top', 'jungle', 'mid', 'adc', 'support']


def train_role():
    role = []
    with open('D:/projects/lol api project alpha/' + 'traning data roles' + '.csv', "r", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        role = reader
        role = pd.DataFrame(role)
    roley = role['realRole']
    role_features = ['championId', 'role', 'lane', 'spell1Id', 'spell2Id']
    role = role.loc[:, role_features]
    role = role.replace(cleanup_roles)
    role = role.apply(pd.to_numeric)
    rolemodel = RandomForestClassifier(max_depth=27, max_features='log2')
    rolemodel.fit(role, roley)
    return rolemodel


def train():
    data = []
    with open('D:/projects/lol api project alpha/' + 'traning data' + '.csv', "r", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data = reader
        data = pd.DataFrame(data)
    data = data.drop('puuid', axis=1)
    data = cleanup_data(data)
    survivor = SVC(kernel='poly', C=5)
    split = DecisionTreeClassifier(max_depth=2)
    turret = LogisticRegression(C=0.01, max_iter=1000000)
    vision = LogisticRegression(C=0.1, max_iter=1000000, solver='newton-cg')
    vision.fit(data.loc[:, class_features[1]], data['visonary'])
    split.fit(data.loc[:, class_features[3]], data['split'])
    survivor.fit(data.loc[:, class_features[0]], data['survivor'])
    turret.fit(data.loc[:, class_features[2]], data['turretdestroyer'])
    return vision, split, survivor, turret


def cleanup_data(data):
    if isinstance(data, list):
        data = pd.DataFrame(data)
        # print(data)
        summoner = data['summonerId'].mode().values[0]
        # print(summoner)
        data = data[data['summonerId'] == summoner]
        data = data.replace(cleanup_roles_list)
    else:
        data = data.replace(cleanup_roles)
    data = data.drop(
        ['platformId', 'gameId', 'summonerId', 'participantId', 'teamId', 'accountId', 'currentPlatformId',
         'currentAccountId', 'matchHistoryUri', 'summonerName', 'profileIcon', 'combatPlayerScore',
         'objectivePlayerScore', 'totalPlayerScore', 'totalScoreRank', 'playerScore0', 'playerScore1', 'playerScore2',
         'playerScore3', 'playerScore4', 'playerScore5', 'playerScore6', 'playerScore7', 'playerScore8',
         'playerScore9', 'sightWardsBoughtInGame'], axis=1)
    data = data.apply(pd.to_numeric)
    data.fillna(0.0, inplace=True)
    X = data.loc[:, ['championId', 'role', 'lane', 'spell1Id', 'spell2Id']]
    real_role = role.predict(X)
    data['role'] = real_role
    return data


def predict(data):
    df = cleanup_data(data)
    df['visonary'] = vision.predict(df.loc[:, class_features[1]])
    df['turretdestroyer'] = turret.predict(df.loc[:, class_features[2]])
    df['split'] = (split.predict(df.loc[:, class_features[3]]))
    df['survivor'] = survivor.predict(df.loc[:, class_features[0]])
    result_to_normal = {'visonary': {2: -1},
                        'survivor': {2: -1}}
    df = df.replace(result_to_normal)
    # print(df[['visonary', 'turretdestroyer', 'split', 'survivor']],
    #       df[['visonary', 'turretdestroyer', 'split', 'survivor']].mean())
    result = df[['visonary', 'turretdestroyer', 'split', 'survivor']].mean()
    if result['visonary'] > 0.5:
        result['visonary'] = 1
    elif result['visonary'] < -0.3:
        result['visonary'] = -1
    else:
        result['visonary'] = 0
    if result['turretdestroyer'] > 0.43:
        result['turretdestroyer'] = 1
    else:
        result['turretdestroyer'] = 0
    if result['split'] > 0.2:
        result['split'] = 1
    else:
        result['split'] = 0
    if result['survivor'] > 0.2:
        result['survivor'] = 1
    elif result['survivor'] < -0.2:
        result['survivor'] = -1
    else:
        result['survivor'] = 0
    return result


role = train_role()
vision, split, survivor, turret = train()
