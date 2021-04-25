
import json


f = open('./data/player_ids.json',)
data = json.load(f)

tmp = {}
for name, id in data.items():
    tmp[id[0]] = name

f.close()

print(tmp)

