from portfolio.performance import returns_dataframe
from utils.etl.sql_server import sql_query
import statsmodels.api as sm


# Read in sql code
prices = sql_query('SELECT * FROM prices').sort_values('Date')

returns_df = returns_dataframe(prices)

### NEED TO DEFINE INDEPENDENT VARIABLES - ADD IN AGE CATEGORY VARIABLE ###
### ALSO CONVERT TO JUPYTER NOTEBOOK ###

X = returns_df[['Name', 'Country', 'Team', 'Position']]
Y = returns_df['Returns_%']

X = sm.add_constant(X)

model = sm.OLS(Y, X).fit()
predictions = model.predict(X)

print_model = model.summary()
print(print_model)
