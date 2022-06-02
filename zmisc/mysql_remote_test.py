from utils.etl.sql_server import sql_query, dataframe_to_sql

# Get all data and upload to main server
df = sql_query('select * from media_buzz')

check = df.groupby('Date').sum()

# Upload to server
dataframe_to_sql(df, 'media', if_exists='replace')
