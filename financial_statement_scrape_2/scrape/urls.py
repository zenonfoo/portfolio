import requests
from bs4 import BeautifulSoup
from typing import List

starting_url = 'https://www.sec.gov'


def get_page(url: str) -> BeautifulSoup:
    return BeautifulSoup(requests.get(url).content, 'html.parser')


def get_list_of_links_to_filing_details(url: str) -> List[str]:
    links = get_page(url).find_all('a', {'id': 'documentsbutton'})
    return [item.get('href') for item in links]


def get_final_financial_statement_link(link: str) -> str:
    page = get_page(starting_url + link)
    all_cells = page.find_all('td')
    index = 0

    for i, cell in enumerate(all_cells):
        if "10-K" in cell.get_text() or cell.get_text() == "":
            index = i + 1
            break

    if index == 0:
        raise Exception("Could not find link for: ", link)
    else:
        try:
            final_url = starting_url + all_cells[index].find('a').get('href')
            print(final_url.replace('ix?doc=/', ''))
            return final_url.replace('ix?doc=/', '')
        except:
            return None


def get_links(url: str) -> List[str]:
    list_of_links = get_list_of_links_to_filing_details(url)
    return list(map(get_final_financial_statement_link, list_of_links))
