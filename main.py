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

print("Response: " + str(response))
print("Matches: " + str(matches))

allStats = []
for game in actuallyNew:
    matchData = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/{game}?api_key={API_KEY}")
    print(game + " added to spreadsheet")
    allStats.append(["Name", "Champion", "Kills", "Deaths", "Assists", "KDA", "CS", "Damage", "First Blood", "Vision Score", "Wards Placed", "Wards Killed", "Pink Wards", "Role", "Team ID", "Game Length", "Game Result", "Side"])
    for i in range(0, 10):
        playerData = matchData.json()['info']['participants'][i]
        row = [playerData['summonerName'], playerData['championName'], playerData['kills'],
        playerData['deaths'], playerData['assists'], kda(playerData['kills'], playerData['deaths'], playerData['assists']), playerData['totalMinionsKilled'], 
        playerData['totalDamageDealtToChampions'], playerData['firstBloodKill'], playerData['visionScore'], 
        playerData['wardsPlaced'], playerData['wardsKilled'], playerData['visionWardsBoughtInGame'], playerData['lane'], 0, matchData.json()['info']['gameDuration'], playerData['win'], playerData['teamId']]
        allStats.append(row)

with open("stats.csv", "a", newline='') as f:
    writer = csv.writer(f)
    writer.writerows(allStats)
f.close()

f = open("gameList.txt", "w")
for n in pastGames:
    f.write(n + "\n")
f.close()

