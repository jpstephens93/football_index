from utils.etl.sql_server import sql_query
import pandas as pd
import datetime as dt


prices = sql_query('SELECT * FROM prices').sort_values('Date')
media = sql_query('SELECT * FROM media').sort_values('Date')

# Footy
footy = prices.groupby('Date').sum().reset_index().rename(columns={'Price': 'Footy'})

# Merge on to prices
prices = pd.merge(prices, footy, 'left', 'Date')

# Filter out mb winners
# winners = media[media['Rank'] <= 3].reset_index(drop=True)
winners = media[(media['MediaBuzz'] <= 1000) & (media['Rank'] <= 3)].reset_index(drop=True)

returns = []
for i in range(len(winners)):
    # Identify player and the date
    dte = winners.loc[i, 'Date'] + dt.timedelta(1)
    player = winners.loc[i, 'ID']
    # 5D
    prices_filtered_5 = prices[(prices['ID'] == player) & (prices['Date'] >= dte)].head(5)
    returns_5 = ((prices_filtered_5['Price'].iloc[-1] / prices_filtered_5['Price'].iloc[0]) - 1)
    relative_5 = returns_5 - ((prices_filtered_5['Footy'].iloc[-1] / prices_filtered_5['Footy'].iloc[0]) - 1)
    # 10D
    prices_filtered_10 = prices[(prices['ID'] == player) & (prices['Date'] >= dte)].head(10)
    returns_10 = ((prices_filtered_10['Price'].iloc[-1] / prices_filtered_10['Price'].iloc[0]) - 1)
    relative_10 = returns_10 - ((prices_filtered_10['Footy'].iloc[-1] / prices_filtered_10['Footy'].iloc[0]) - 1)
    # 15D
    prices_filtered_15 = prices[(prices['ID'] == player) & (prices['Date'] >= dte)].head(15)
    returns_15 = ((prices_filtered_15['Price'].iloc[-1] / prices_filtered_15['Price'].iloc[0]) - 1)
    relative_15 = returns_15 - ((prices_filtered_15['Footy'].iloc[-1] / prices_filtered_15['Footy'].iloc[0]) - 1)

    returns.append([dte, player, relative_5, relative_10, relative_15])

returns_df = pd.DataFrame(returns, columns=['Date', 'Player', 'Relative 5D', 'Relative 10D', 'Relative 15D'])

for col in returns_df.columns[-3:]:
    rets = round(100 * (len(returns_df[returns_df[col] > 0][col]) / len(returns_df)), 2)
    print(col + ': ' + str(rets) + '%')
