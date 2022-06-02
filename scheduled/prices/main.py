import sys
sys.path.append('C:/Users/User/PycharmProjects/FootballIndex/')
from utils.etl.sql_server import dataframe_to_sql
from utils.etl.http_requests import get_dataframe
from utils.message.email import send_email
import pandas as pd
import datetime as dt

dte = dt.date.today()

# Define T200 & Squad list API args
first_team = 'football.all?page=1&per_page=200'
squad = 'football.allTradable?page=1&per_page=5000'

first_team_df = get_dataframe(first_team)
squad_df = get_dataframe(squad)

df = first_team_df.append(squad_df).reset_index(drop=True)

positions = [player['second']['name'] for player in df['sectors']]

# Add player position
df['position'] = positions

df = df[['name', 'optaid', 'id', 'urlname', 'country', 'team', 'position', 'price']]

# Add date column
df['date'] = dte

# Add full web address to urlname
df['urlname'] = 'https://www.footballindex.co.uk/player/' + df['urlname']

# Order & rename remaining columns
df = df[['date', 'name', 'optaid', 'id', 'urlname', 'country', 'team', 'position', 'price']]
col_names = ['Date', 'Name', 'OptaID', 'ID', 'URL', 'Country', 'Team', 'Position', 'Price']

df.columns = col_names

# Upload to sql
dataframe_to_sql(df, 'prices')

# Send email to confirm
send_email(
    me=pd.read_json('user_password.json')['user'],
    p_word=pd.read_json('user_password.json')['password'],
    to=pd.read_json('user_password.json')['user'],
    subject='FI Prices - Success'
)
