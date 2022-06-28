from selenium import webdriver
from yahoo.scrape_quarterly import get_data
from yahoo.calc import calc
import pandas as pd
import time
from yahoo.calc import YearlyQuarterly

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 1000)

PATH = '/Users/zenonfoo/Documents/DevTools/chromedriver/chromedriver'
driver = webdriver.Chrome(PATH)
driver.get('https://uk.finance.yahoo.com/')
time.sleep(1)
button = next(filter(lambda x: x.text == 'I agree', driver.find_elements_by_tag_name('button')))
button.click()


def dp_2(val):
    try:
        return round(val, 2)
    except:
        return val


def thousand_separator(val):
    try:
        return "{:,}".format(val)
    except:
        return val


result = calc(get_data(driver, '5007.KL'), YearlyQuarterly.QUARTERLY)
print(result['summary_data'].applymap(dp_2).applymap(thousand_separator))
