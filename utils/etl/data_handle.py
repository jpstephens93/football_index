import pandas as pd


def remove_duplicated_data(df):
    """
    Short function that takes in a DataFrame, removes duplicates, and spits out new DataFrame
    :param df: pandas DataFrame
    :return: df without the duplicates
    """
    df['temp_id'] = df['Date'].astype('str') + df['ID']

    return df.drop_duplicates('temp_id').drop(columns='temp_id')


def timeseries_dates(prices_df):
    """
    Takes prices_df from Football Index database and returns dictionary of dates, between which are the dates that need
    to be filled in the timeseries
    :param prices_df: DataFrame of Football Index prices
    :return: dates, dict, of dates to be filled between
    """
    assert (prices_df.shape[1] == 9), "Ensure DataFrame being fed is prices_df; column count not equal to 9"
    grouped = prices_df.groupby('Date').sum().reset_index()
    grouped['date_diff'] = (grouped['Date'] - grouped['Date'].shift()).dt.days
    grouped = grouped.dropna().reset_index(drop=True)
    outliers = grouped[grouped['date_diff'] != 1]
    rows = outliers.index.values
    dates = {}
    for r in rows:
        dates[grouped.iloc[r]['Date']] = grouped.iloc[r - 1]['Date']
    return dates


def returns_dataframe(prices_df):
    """
    Quick function that takes in a prices dataframe as argument and returns a transposed returns dataframe
    """
    player_prices_matrix = prices_df.pivot_table('Price', 'Date', 'Name').fillna(method='bfill', inplace=True)

    player_returns = pd.DataFrame(((player_prices_matrix.iloc[-1] / player_prices_matrix.iloc[0]) - 1) * 100).round(2)
    player_returns.sort_values(0, ascending=False).reset_index(inplace=True)
    player_returns.columns = ['Name', 'Returns_%']

    df = prices_df.drop_duplicates('Name')[['Name', 'Country', 'Team', 'Position']]

    return df.merge(player_returns, 'left', 'Name')
