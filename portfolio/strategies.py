import pandas as pd


def golden_boys():
    # Data
    fifa_data = pd.read_csv('C:/Users/User/Desktop/Projects/FootballIndex/portfolio/excel/fifa_2020.csv')

    # Filter universe applying quant-based rules
    universe = fifa_data[
        (fifa_data['age'] <= 24) & (fifa_data['potential'] >= 90) & (fifa_data['difference'] >= 5)
    ][['name', 'nationality', 'team', 'overall', 'potential', 'difference']].sort_values('potential', ascending=False)

    return universe
