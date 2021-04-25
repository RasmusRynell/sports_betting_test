import sqlite3
from sqlalchemy import create_engine
import pandas as pd
import requests
import json

cur = sqlite3.connect('./database.db')

test = requests.get("https://statsapi.web.nhl.com/api/v1/teams").json()

df = pd.DataFrame.from_dict(test["teams"])
print(df.columns)
df = df.drop(columns=['venue', 'division', 'conference', 'franchise'])
print(df.columns)

df.to_sql("team", cur, if_exists='replace')
#print(json.dumps(keep, indent=4))
