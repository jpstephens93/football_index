from utils.etl.sql_server import sql_query
import pandas as pd


def vol_dataframe(prices):
    """
    Quick function that takes in a prices dataframe as argument and returns a transposed returns dataframe
    """
    player_prices_matrix = prices.pivot_table('Price', 'Date', 'Name').fillna(method='bfill')
    returns = (player_prices_matrix.pct_change() * 100).dropna()

    player_vol = pd.DataFrame(returns.std()).reset_index().rename(columns={0: "Standard_Deviation_%"})

    df = prices.drop_duplicates('Name')[['Name', 'Country', 'Team', 'Position']]

    return df.merge(player_vol, 'left', 'Name')


prices = sql_query('select * from footballindex.prices')
volatility = vol_dataframe(prices)

# View vol by country, team, position
country_vol = volatility.groupby('Country').mean()
team_vol = volatility.groupby('Team').mean()
position_vol = volatility.groupby('Position').mean()

portfolio = pd.read_json('portfolio/json/portfolio_20201107.json', lines=True)

merged = pd.merge(portfolio, volatility[['Name', 'Standard_Deviation_%']], 'left', 'Name')
