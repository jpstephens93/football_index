from utils.etl.sql_server import read_sql_file, sql_query
from portfolio.strategies import golden_boys
import pandas as pd
import datetime as dt

dte = dt.date.today()

# Read in football index data for player info
fi_data = sql_query(read_sql_file('zmisc/sql/player_universe.sql'))
# Define strategy
strategy = golden_boys()
# Calculate weighting factors
portfolio = pd.merge(
    fi_data,
    strategy,
    'inner',
    left_on='Name',
    right_on='name'
).drop(columns='Name').sort_values('overall').reset_index(drop=True).reset_index()
portfolio['index'] = pd.to_numeric(portfolio['index'] + 1)

# Overall rating weight factor
portfolio['overall_wt'] = portfolio['index'] / sum(portfolio['index'])
# (Potential - Current) ability difference weight factor
portfolio['difference_wt'] = portfolio['difference'] / sum(portfolio['difference'])
# Combine both weighting factors for portfolio weights
portfolio['weight'] = (portfolio['difference_wt'] + portfolio['overall_wt']) / 2

portfolio = portfolio[['name', 'weight']].sort_values('weight', ascending=False)
portfolio.columns = ['Name', 'Weight']

# Output portfolio to json
portfolio.to_json(f'portfolio/json/portfolio_{dte.strftime("%Y%m%d")}.json', 'records', lines=True)
