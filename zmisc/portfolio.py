from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

import pandas as pd
import time


class Portfolio:
    
    USER = pd.read_json('user_password.json')['user']
    PASSWORD = pd.read_json('user_password.json')['password']

    def __init__(self, deposit):
        self.login_page = "https://www.footballindex.co.uk/top-200?login"
        self.deposit = deposit

        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def login(self):
        driver = self.driver
        driver.get(self.login_page)
        driver.set_page_load_timeout(10)
        time.sleep(5)

        username = driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[1]/div/div/div[2]/div/form/div[1]/div[1]/input"
        )
        username.send_keys(self.USER)
        password = driver.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div/form/div[1]/div[2]/input"
        )
        password.send_keys(self.PASSWORD)
        time.sleep(3)

        driver.find_element_by_id("login").click()
        driver.set_page_load_timeout(10)
        time.sleep(3)

    def positions(self):
        try:
            self.login()
        except WebDriverException:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
            self.login()

        self.driver.get("https://www.footballindex.co.uk/portfolio")
        self.driver.set_page_load_timeout(10)
        time.sleep(5)

        pf_list = self.driver.find_element_by_class_name('List__list___1IoeR').text.splitlines()

        try:
            pf_dict = {
                'players': [pf_list[i] for i in range(0, len(pf_list), 8)],
                'shares': [pf_list[i] for i in range(1, len(pf_list), 8)],
                'unit_cost': [pf_list[i].replace('£', '') for i in range(2, len(pf_list), 8)],
                'cost': [pf_list[i].replace('£', '') for i in range(3, len(pf_list), 8)],
                'price': [pf_list[i].replace('£', '') for i in range(4, len(pf_list), 8)],
                'value': [pf_list[i].replace('£', '') for i in range(5, len(pf_list), 8)]
            }
        except ValueError:
            pf_dict = {
                'players': [pf_list[i] for i in range(1, len(pf_list), 12)],
                'shares': [pf_list[i] for i in range(2, len(pf_list), 12)],
                'unit_cost': [pf_list[i].replace('£', '') for i in range(4, len(pf_list), 12)],
                'cost': [pf_list[i].replace('£', '') for i in range(5, len(pf_list), 12)],
                'price': [pf_list[i].replace('£', '') for i in range(6, len(pf_list), 12)],
                'value': [pf_list[i].replace('£', '') for i in range(7, len(pf_list), 12)]
            }

        pf = pd.DataFrame(pf_dict)
        for col in pf.iloc[:, 1:].columns:
            pf[col] = pd.to_numeric(pf[col])

        self.driver.close()

        return pf

    def cash_balance(self):
        try:
            self.login()
        except WebDriverException:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
            self.login()

        self.driver.get("https://www.footballindex.co.uk/portfolio")
        self.driver.set_page_load_timeout(10)
        time.sleep(5)

        balance = float(
            self.driver.find_element_by_class_name('Balance__container___2bfAL').text.splitlines()[-1].replace('£', '')
        )

        self.driver.close()

        return balance

    def total_value(self):
        cash = self.cash_balance()
        value = self.positions()['value'].sum()

        return cash + value


def rebalance(positions, total_capital, json_file, cash_position=0.05):
    """
    MAKE SURE POSITIONS IS PORTFOLIO DATAFRAME
    :param cash_position: Desired cash % position in portfolio
    :param positions: Must be portfolio format
    :param total_capital: Amount committed in fund
    :param json_file: Name of portfolio json file
    :return: buys, sells dataframe
    """
    assert isinstance(json_file, str), "Ensure json_file is of type string"
    portfolio_json = pd.read_json(f'portfolio/json/{json_file}.json', lines=True)

    new_pf = pd.merge(positions, portfolio_json, how='outer', left_on='players', right_on='Name')

    new_pf['new_cost'] = new_pf['Weight'] * total_capital * (1 - cash_position)
    new_pf['new_shares'] = pd.to_numeric(round(new_pf['new_cost'] / new_pf['price']), downcast='integer')
    new_pf['buy_sell'] = new_pf['new_shares'] - new_pf['shares']

    print(new_pf[new_pf['buy_sell'] != 0][['players', 'shares', 'new_shares', 'buy_sell']].sort_values('buy_sell'))

    buys = new_pf[new_pf['buy_sell'] > 0][['players', 'buy_sell', 'price']]
    sells = new_pf[new_pf['buy_sell'] < 0][['players', 'buy_sell', 'price']]

    for frame in [buys, sells]:
        frame['cost'] = frame['buy_sell'] * frame['price']

    return buys, sells
