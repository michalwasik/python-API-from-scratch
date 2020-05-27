import json
with open('/home/t440/PycharmProjects/race_times/track.json', 'r') as json_file:
    json_data = json.load(json_file)
for i in json_data:
    if i['name'].lower() == 'abbazia'.lower():
        print(i['data'])