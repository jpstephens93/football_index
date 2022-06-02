from zmisc.portfolio import rebalance
from utils.etl.sql_server import read_sql_file, sql_query

from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import pandas as pd
import datetime as dt

dte = (dt.date.today() - dt.timedelta(1)).strftime("%Y-%m-%d")

driver = webdriver.Chrome(ChromeDriverManager().install())

# Log in to footy index account
login_page = "https://www.footballindex.co.uk/top-200?login"

driver.get(login_page)
driver.set_page_load_timeout(10)
sleep(5)

assert "Football Index" in driver.title

user = pd.read_json('user_password.json')['user']
pword = pd.read_json('user_password.json')['password']

username = driver.find_element_by_xpath(
    "/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div/form/div[1]/div[1]/input"
)
username.send_keys(user)
password = driver.find_element_by_xpath(
    "/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div/form/div[1]/div[2]/input"
)
password.send_keys(pword)

driver.find_element_by_id("login").click()
driver.set_page_load_timeout(10)
sleep(3)

# Get positions
driver.get("https://www.footballindex.co.uk/portfolio")
driver.set_page_load_timeout(10)
sleep(5)

pf_list = driver.find_element_by_class_name('List__list___1IoeR').text.splitlines()


def compile_portfolio(i=[0, 1, 2, 3, 4, 5], step=8):
    """
    Quick function to return dictionary of portfolio positions
    :param i: list range of scraping parameters which vary based on machine i.e. Windows, Mac, Linux
    :param step: ditto above but the step
    :return: dict of current portfolio
    """
    try:
        return {
            'players': [pf_list[x] for x in range(i[0], len(pf_list), step)],
            'shares': [pf_list[x] for x in range(i[1], len(pf_list), step)],
            'unit_cost': [pf_list[x].replace('£', '') for x in range(i[2], len(pf_list), step)],
            'cost': [pf_list[x].replace('£', '') for x in range(i[3], len(pf_list), step)],
            'price': [pf_list[x].replace('£', '') for x in range(i[4], len(pf_list), step)],
            'value': [pf_list[x].replace('£', '') for x in range(i[5], len(pf_list), step)]
        }
    except ValueError:
        print("Ensure you have calibrated for correct machine (i.e. Windows, Mac, Linux)")


pf_dict = compile_portfolio()

pf = pd.DataFrame(pf_dict)

for col in pf.iloc[:, 1:].columns:
    pf[col] = pd.to_numeric(pf[col])

# Get cash balance
cash_balance = float(
    driver.find_element_by_class_name('Balance__container___2bfAL').text.splitlines()[-1].replace('£', '')
)

value = cash_balance + pf['value'].sum()

buys, sells = rebalance(pf, value, 'portfolio', 0.01)

# Fetch player URL's
urls = sql_query(
    read_sql_file('zmisc/sql/player_info.sql', {'fi_table': 'prices', 'dte': f'"{dte}"'})
)


def buy_and_sell(buy_or_sell, quantity):
    """
    Function to perform buying and selling, depending on which direction is specified as variable
    :param quantity: number of shares to buy or sell
    :param buy_or_sell: string of buy or sell
    :return: N/A - performs buying and selling with given driver
    """
    assert (buy_or_sell == 'buy') | (buy_or_sell == 'sell'), "Variable 'buy_or_sell' must be either 'buy' or 'sell'"
    button = driver.find_element_by_id(buy_or_sell)
    button.click()
    sleep(4)

    if buy_or_sell == 'buy':
        now = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div/div[4]/div[2]/button[1]')
    else:
        now = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div/div[4]/div[2]/button[2]')
    now.click()
    sleep(4)

    shares_box = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div/div[8]/input')
    shares_box.send_keys(Keys.CONTROL, 'a')
    shares_box.send_keys(Keys.DELETE)
    shares_box.send_keys(str(quantity))
    sleep(4)

    if buy_or_sell == 'buy':
        buy_sell = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div/div[9]/button[2]')
    else:
        buy_sell = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div/div[10]/button[2]')
    buy_sell.click()
    sleep(4)

    if buy_or_sell == 'buy':
        px_movement = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div/div[8]/div[2]/label')
    else:
        px_movement = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div/div[10]/div[2]/label')
    px_movement.click()
    sleep(4)

    if buy_or_sell == 'buy':
        complete = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div/div[9]/button[2]')
    else:
        complete = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div/div[11]/button[2]')
    complete.click()


for frame in [buys, sells]:
    frame = pd.merge(frame, urls, 'left', left_on='players', right_on='Name')
    for order, link in zip(frame['buy_sell'], frame['URL']):
        driver.get(link)
        driver.set_page_load_timeout(10)
        sleep(4)
        if order > 0:
            buy_and_sell('buy', abs(order))
        else:
            buy_and_sell('sell', abs(order))

driver.close()
