from utils.etl.data_handle import remove_duplicated_data
from utils.etl.sql_server import sql_query, read_sql_file, dataframe_to_sql


prices = sql_query(read_sql_file('zmisc/sql/all_player_prices.sql'))
media = sql_query(read_sql_file('zmisc/sql/all_player_media.sql'))

# Remove all duplicates
prices = remove_duplicated_data(prices)
media = remove_duplicated_data(media)

# Check
check = prices.groupby('Date').sum()
(1 + check.pct_change()[1:]).cumprod().plot()

# Interpolate missing dates


# Re-upload data to SQL
dataframe_to_sql(media, 'media_buzz', if_exists='replace')
