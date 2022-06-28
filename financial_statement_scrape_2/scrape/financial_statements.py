import urllib.request
from bs4 import BeautifulSoup
from typing import List, Tuple
import codecs


def get_page(url: str) -> BeautifulSoup:
    with urllib.request.urlopen(url) as response:
        html = response.read()
    return BeautifulSoup(html, 'html.parser')


def get_local_page(path: str) -> BeautifulSoup:
    html = codecs.open(path, 'r')
    return BeautifulSoup(html.read(), 'html.parser')


def check_for_tag_and_headers(list_to_check: List[Tuple[str, str, str, str]], page: BeautifulSoup) -> \
        Tuple[str, str, str, str]:
    for to_check in list_to_check:
        tag = to_check[0]
        headers = to_check[1:]
        all_tags = page.find_all(tag)
        check = set()
        for tag in all_tags:
            tag_texts = [x.strip().lower() for x in tag.get_text().split('  ')]
            for tag_text in tag_texts:
                if any([tag_text == x for x in headers]):
                    check.add(tag_text)
                    if len(check) == 3:
                        return to_check

    raise Exception("check_for_tags_and_headers_found_nothing")


def construct_table(data: BeautifulSoup) -> List[List[str]]:
    data_store = []

    try:
        for row in data.find_all('tr'):
            data_store.append([cols.text for cols in row.find_all('td')])
            data_store.append([cols.text for cols in row.find_all('th')])
    except:
        data_store.append(None)

    return data_store


def get_table(all_tags: List[BeautifulSoup], index: int) -> Tuple:
    table_not_found = True
    counter = 1
    while table_not_found:
        index_to_check = index + counter
        if all_tags[index_to_check].name == 'table':
            return all_tags[index_to_check], index_to_check
        else:
            counter += 1


def get_financial_tables_helper(all_tags: List[BeautifulSoup], consolidated_header_names: dict) -> dict:
    processed_tables = 0
    data = {}
    for counter, tag in enumerate(all_tags):
        try:
            indicator: List = [x.strip().lower() for x in tag.get_text().split('  ')]
            # The comments here are hacks for when there are multiple consolidated headers throughout the document and
            # need a second check to make sure it's the header of the intended statement
            # if counter < len(all_tags):
            #     next_tag = all_tags[counter + 1].get_text().strip()
            for key in consolidated_header_names.keys():
                if consolidated_header_names[key] in indicator \
                        and key not in data.keys():
                        # and ('millions' in next_tag or 'thousands' in next_tag):
                        # and ('YEARS ENDED' in next_span or 'In thousands' in next_span):
                    #     This is for when there are tables spread across 2 pages
                    # if consolidated_header_names[key] == 'consolidated balance sheets':
                    #     table1, i = get_table(all_tags, counter)
                    #     table2, i = get_table(all_tags, i)
                    #     table1 = construct_table(table1)
                    #     table2 = construct_table(table2)
                    #     if len(table2) < 10:
                    #         table2, i = get_table(all_tags, i)
                    #         table2 = construct_table(table2)
                    #     data[key] = table1 + table2
                    # else:
                    table, _ = get_table(all_tags, counter)
                    data[key] = construct_table(table)
                    processed_tables += 1
                    break
            if processed_tables == 3:
                return data
        except:
            raise Exception('.get_text() not working! for get_financial_tables_helper')
    raise Exception('Error with get_financial_tables_helper')


def get_financial_tables(all_tags: List[BeautifulSoup], headers: Tuple[str, str, str]):
    consolidated_header_names = {'income_statement': headers[0],
                                 'balance_sheet': headers[1],
                                 'cash_flow': headers[2]}
    return get_financial_tables_helper(all_tags, consolidated_header_names)


def get_financial_statements(url: str, list_to_check: List[Tuple[str, str, str, str]]) -> dict:
    page: BeautifulSoup = get_page(url)
    correct_tag_and_headers = check_for_tag_and_headers(list_to_check, page)
    correct_tags = [correct_tag_and_headers[0], 'table']
    correct_headers = correct_tag_and_headers[1:]
    all_tags: List[BeautifulSoup] = page.find_all(correct_tags)
    financial_tables = get_financial_tables(all_tags, correct_headers)
    return financial_tables
