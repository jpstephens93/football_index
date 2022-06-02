from utils.etl.sql_server import read_sql_file, sql_query


def benchmark_returns(start, end):
    """
    Get benchmark returns from between specified dates
    :param start: str, start date
    :param end: str, end date
    :return: str, percentage return over the period
    """
    assert isinstance(start, str) & isinstance(end, str), "Ensure start and end dates are of type str"
    # Read in sql code & calculate benchmark returns over the period
    benchmark = sql_query(read_sql_file(
        'sql/player_prices.sql',
        {'fi_table': 'prices', 'start_date': '"{}"'.format(start), 'end_date': '"{}"'.format(end)}
    )).groupby('Date').sum()
    # Calculate benchmark returns over the period
    return (((benchmark.iloc[-1] / benchmark.iloc[0]) - 1) * 100).round(2)[0]


def portfolio_returns(portfolio):
    #### THIS NEEDS TO BE DONE ####
    portfolio['actual_value'] = portfolio['value'] * 0.98
    bench_rets = benchmark_returns()

    port_rets = round(((((portfolio['actual_value'].sum() + balance) / deposit) - 1) * 100), 2)
    relative_rets = port_rets - bench_rets

    print("Portfolio Returns (ITD) | {}".format(port_rets))
    print("Benchmark Returns (ITD) | {}".format(self.bench_rets))
    print("-" * 35)
    print("Relative Returns (ITD)  | {}".format(round(relative_rets, 2)))
