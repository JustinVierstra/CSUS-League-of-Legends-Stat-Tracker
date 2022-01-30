from operator import indexOf
from types import resolve_bases
from dotenv import load_dotenv
import requests
import csv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

while not API_KEY:
    url = "https://developer.riotgames.com/"
    print(f"Keys can be generated: {url}")
    API_KEY = input("Please provide an api key:")

name = input("Enter summoner name: ")
queue = int(input("QUEUE TYPE:\n0: Tournament Customs\n2: Blind Pick Normals\n65: Aram\n400: Draft Pick Normals\n420: Ranked\nEnter Queue Number: "))

while(queue !=0 and queue != 2 and queue != 65 and queue != 400 and queue != 420):
    queue = int(input("Please enter a valid number: "))

response = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}?api_key={API_KEY}")

puuid = response.json()['puuid']

matches = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={queue}&count=10&api_key={API_KEY}")

championList = requests.get("http://ddragon.leagueoflegends.com/cdn/12.2.1/data/en_US/champion.json")
crd = championList.json()['data']

def getChampName(id):
    for i in crd:
        if(crd[i]["key"] == str(id)):
            return i

print("Response: " + str(response))
print("Matches: " + str(matches))

possibleNewGames = []
possibleNewGames = matches.json()
pastGames = []
actuallyNew = []

exists = os.path.exists('gameList.txt')

if(exists):
    f = open('gameList.txt', "r")
    lines = f.readlines()
    f.close()

    for line in lines:
        pastGames.append(line.strip())

if pastGames:
    for i in possibleNewGames:
        if i in pastGames:
            print(i + " already in spreadsheet")
        else:
            pastGames.append(i)
            actuallyNew.append(i)
else:
    actuallyNew = possibleNewGames
    pastGames = possibleNewGames
        
def kda(k,d,a):
    return round((k + a)/d,2) if d else round((k + a)/1, 2)

def gameResult(result):
    if result == True:
        return 1
    return 0

def firstBlood(first_blood):
    if first_blood == True:
        return 1
    return 0

def kp(kills, assists, team):
    if(team<5):
        return str(round((kills+assists)/side1TotalKills*100, 2)) + "%"
    else:
        return str(round((kills+assists)/side2TotalKills*100, 2)) + "%"

def side(whichSide):
    if whichSide == 100:
        return "Red"
    else:
        return "Blue"
        
def role(roleId):
    if roleId == 0:
        return "Top"
    elif roleId == 1:
        return "Jungle"
    elif roleId == 2:
        return "Mid"
    elif roleId == 3:
        return "Adc"
    elif roleId == 4:
        return "Support"


allStats = []
count = 0
allStats.append(["Player Name:", "Champion:", "Kills:", "Deaths:", "Assists:", "KDA:", "KP:", "CS:", "Damage:", "Gold Earned:", "First Blood:", "Vision Score:", "Wards Placed:", "Wards Killed:", "Pink Wards:", "Role:", "Team ID:", "Game Length:", "Game Result:", "Side:", "", "Bans:"])
for game in actuallyNew:
    matchData = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/{game}?api_key={API_KEY}")
    print(game + " added to spreadsheet")
    if count!=0:
        allStats.append([])
    else:
        count+=1
    side1TotalKills = 0
    side2TotalKills = 0

    gameDuration = round((matchData.json()['info']['gameDuration'])/60,2)

    for i in range(0,10):
        playerData = matchData.json()['info']['participants'][i]

        if(i<5):
            side1TotalKills += playerData['kills']
        elif(i<10):
            side2TotalKills += playerData['kills']

    for i in range(0, 10):
        playerData = matchData.json()['info']['participants'][i]
        if(i<5):
            banData = matchData.json()['info']['teams'][0]['bans'][i]['championId']
        else:
            banData = matchData.json()['info']['teams'][1]['bans'][i%5]['championId']
        row = [playerData['summonerName'].center(15), playerData['championName'], playerData['kills'],
        playerData['deaths'], playerData['assists'], kda(playerData['kills'], playerData['deaths'], playerData['assists']), kp(playerData['kills'],playerData['assists'], i),playerData['totalMinionsKilled'] + playerData['neutralMinionsKilled'], 
        playerData['totalDamageDealtToChampions'], playerData['goldEarned'], firstBlood(playerData['firstBloodKill']), playerData['visionScore'], 
        playerData['wardsPlaced'], playerData['wardsKilled'], playerData['visionWardsBoughtInGame'], role(i%5), 0, gameDuration, gameResult(playerData['win']), side(playerData['teamId']), "", getChampName(banData)]
        allStats.append(row)



with open("stats.csv", "a", newline='') as f:
    writer = csv.writer(f)
    writer.writerows(allStats)
f.close()

f = open("gameList.txt", "w")
for n in pastGames:
    f.write(n + "\n")
f.close()

