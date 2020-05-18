from bs4 import BeautifulSoup
import requests
import json


r = requests.get('https://www.racingcircuits.info/a-to-z-circuit-list.html?fbclid=IwAR0dFN6zqcJU011CQVlumPKNI6jK-lSKcWjV1GoRVkl0PwdnFqIQqmeXFYQ')
soup = BeautifulSoup(r.text, 'html.parser')
tracks = []

for el in soup.find_all("div", {"class": "az-item"}):
    tracks.append(el.get_text().strip())

tracks_dict = []
for i in tracks:
    if 'See More' not in i:
        tracks_dict.append({'name': i, 'data': []})

with open("track.json", "r") as jsonFile:
    data_json = json.load(jsonFile)
print(data_json)

if data_json != tracks_dict:
    with open("track.json", "w") as jsonFile:
        json.dump(tracks_dict, jsonFile)
