from utils.etl.sql_server import read_sql_file, sql_query
from utils.etl.data_handle import returns_dataframe
import pandas as pd
from datetime import date


def backtester(start_date=None, end_date=None, json_file='portfolio'):
    """
    Backtest function that takes start & end dates and returns results explaining how the model portfolio would have
    performed within that window, both on an absolute and relative basis.

    :param json_file: str, name of the json file to read portfolio from
    :param start_date: str, start date of backtest
    :param end_date: str, end date of backtest
    :return: Print statements of backtest result
    """

    if start_date is None:
        start_date = '2000-01-01'
    if end_date is None:
        end_date = date.today().strftime('%Y-%m-%d')

    # Read in sql code
    sql = read_sql_file(
        'analysis/backtest/sql/prices_between_dates.sql',
        {'fi_table': 'prices', 'start_date': '"{}"'.format(start_date), 'end_date': '"{}"'.format(end_date)}
    )

    prices_df = sql_query(sql)
    returns_df = returns_dataframe(prices_df)

    # Calculate portfolio returns over the period
    pf = pd.read_json('portfolio/json/{}.json'.format(json_file), lines=True)
    portfolio = pd.merge(
        pf,
        returns_df[['Name', 'Returns_%']],
        'left',
        'Name'
    ).fillna(0).sort_values('Returns_%', ascending=False)

    # Save down backtest result
    try:
        portfolio.to_excel('portfolio/excel/backtest_result.xlsx', index=False)
    except PermissionError:
        print('Close the open instance of backtest result Excel file and rerun')

    assert round(sum(portfolio['Weight']), 2) == 1, "Portfolio weights don't sum to 100% - check JSON file"

    if len(portfolio) != len(pf):
        raise ValueError("Names in the portfolio json file are incorrect: {}".format(
            list(pf[~pf['Name'].isin(portfolio['Name'])]['Name']))
        )

    portfolio_returns = round(sum(portfolio['Weight'] * portfolio['Returns_%']), 2)

    # Calculate benchmark returns over the period
    benchmark = prices_df.groupby('Date').sum()
    benchmark_returns = round((100 * sum(pd.to_numeric(benchmark.pct_change()[1:]['Price']))), 2)

    # Summarise & print results
    print('BACKTEST COMPLETE')
    print('-----------------')
    print('Start Date: {}'.format(start_date))
    print('End Date: {}'.format(end_date))
    print('-----------------')
    print('PERFORMANCE')
    print('Portfolio: {}'.format(str(round(portfolio_returns, 2)) + '%'))
    print('Benchmark: {}'.format(str(round(benchmark_returns, 2)) + '%'))
    print('Relative: {}'.format(str(round(portfolio_returns - benchmark_returns, 2)) + '%'))
    print('-----------------')
    print('TOP 5:')
    print(portfolio.reset_index(drop=True).head())
    print('BOTTOM 5:')
    print(portfolio.reset_index(drop=True).tail())


# Backtest portfolio
backtester(start_date='2020-09-01', end_date='2020-09-30', json_file='portfolio.json')
