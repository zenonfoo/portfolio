from selenium import webdriver
import time

result = []
PATH = '/Users/zenonfoo/Documents/DevTools/chromedriver/chromedriver'
driver = webdriver.Chrome(PATH)
driver.get('https://www.nyse.com/listings_directory/stock')

for i in range(775):
    table = driver.find_element_by_class_name('table')
    rows = table.find_elements_by_tag_name('tr')
    for row in rows[1:]:
        row_split_by_space = row.text.split(' ')
        x = {'ticker': row_split_by_space[0],
             'name': ' '.join(row_split_by_space[1:])}
        result.append(x)

    to_click = [i for i in driver.find_elements_by_tag_name('a') if i.text == 'NEXT ›']
    to_click = to_click[0]
    to_click.click()
    time.sleep(2)
