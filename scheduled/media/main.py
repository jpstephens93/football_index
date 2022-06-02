import sys
sys.path.append('C:/Users/User/PycharmProjects/FootballIndex/')
from utils.etl.sql_server import dataframe_to_sql
from utils.etl.http_requests import get_dataframe
from utils.message.email import send_email
import pandas as pd
import datetime as dt

# Define the date range of the data to be scraped
dte = dt.date.today() - dt.timedelta(1)

# Get Buzz API into DataFrame
media_buzz = "buzzmedia/rankedpage/footballuk.all:{}?page=1&per_page=1000&sort_direction=desc&sort_field=score".format(
    dte.strftime('%Y%m%d')
)

df = get_dataframe(media_buzz)[['name', 'optaid', 'id', 'urlname', 'rank', 'score']]

# Add full web address to urlname
df['urlname'] = 'https://www.footballindex.co.uk/player/' + df['urlname']
df['date'] = dte

# Get appropriate columns
df = df[['date', 'name', 'optaid', 'id', 'urlname', 'rank', 'score']]
df.columns = ['Date', 'Name', 'OptaID', 'ID', 'URL', 'Rank', 'MediaBuzz']

# Clean data
df = df[df['MediaBuzz'] > 10]
df['temp_id'] = df['Date'].astype('str') + df['Name']

df.drop_duplicates('temp_id', inplace=True)
df.drop(columns='temp_id', inplace=True)

# Upload to sql
dataframe_to_sql(df, 'media')

# Send email to confirm
send_email(
    me=pd.read_json('user_password.json')['user'],
    p_word=pd.read_json('user_password.json')['password'],
    to=pd.read_json('user_password.json')['user'],
    subject='FI Media Buzz - Success'
)
