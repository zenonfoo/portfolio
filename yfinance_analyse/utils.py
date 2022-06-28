import pandas as pd
from typing import List
import numpy as np
from models import ProcessedFinancialData
from yahooquery import Ticker
import pprint as pp
import math


def format_num(val):
    try:
        temp = round(val, 2)
        return "{:,}".format(temp)
    except:
        return val


def replace_columns_with_only_year(data: pd.DataFrame):
    cols = data.columns
    new_cols = [col.split('-')[0] for col in cols]
    new_data = data.copy()
    new_data.columns = new_cols
    return new_data


def check_break_row(index: str, data: pd.DataFrame):
    values_for_index_name = data.iloc[index, :].values
    return all([x == '' for x in values_for_index_name])


def get_combined_sorted_years(data: List[pd.DataFrame]) -> List[str]:
    results = []
    for r in data:
        results += list(r.columns)
    results = set(results)
    return sorted(results)


def create_row_data_for_multi_index(total_cols: List[str], data: pd.Series):
    result = []
    for col in total_cols:
        try:
            result.append(data[col])
        except:
            result.append(np.nan)
    return result


def combine_print(data: List[ProcessedFinancialData]):
    data_with_year_only_columns = [replace_columns_with_only_year(d.summary_data) for d in data]
    combined_sorted_years = get_combined_sorted_years(data_with_year_only_columns)
    len_of_combined_sorted_years = len(combined_sorted_years)
    keys = data[0].summary_data.index

    index = []
    values = []

    for i, k in enumerate(keys):
        if check_break_row(i, data[0].summary_data):
            index.append((k, ''))
            values.append([''] * len_of_combined_sorted_years)
        else:
            for d_modified, d in zip(data_with_year_only_columns, data):
                name = d.metadata.get('name')
                index.append((k, name))
                values.append(create_row_data_for_multi_index(combined_sorted_years, d_modified.loc[k]))
            index.append(('', ''))
            values.append([''] * len_of_combined_sorted_years)

    multi_index = [
        [i[0] for i in index],
        [i[1] for i in index]
    ]
    result = pd.DataFrame(values, index=multi_index)
    result.columns = combined_sorted_years
    return result.applymap(format_num)


def compare_latest_years(data: List[ProcessedFinancialData]):
    results = []
    for d in data:
        last_year_data = d.summary_data.iloc[:, -1].copy()
        last_year_data.name = d.metadata['name']
        results.append(last_year_data)
    return pd.concat(results, axis=1).applymap(format_num)


def compare_averages(data: List[ProcessedFinancialData]):
    results = []
    for d in data:
        num_of_years = d.summary_data.shape[1]
        mean_data = d.summary_data.replace('', 0).replace('-', np.nan).mean(axis=1).replace(0, '').replace(np.nan, '-')
        mean_data.name = d.metadata['name'] + ' - {} yrs'.format(num_of_years)
        results.append(mean_data)
    return pd.concat(results, axis=1).applymap(format_num)


def print_summary(d: ProcessedFinancialData, index=0):
    pretty_printer = pp.PrettyPrinter()
    ticker = d.metadata['ticker']
    metadata = d.metadata
    market_cap = list(Ticker(ticker).summary_detail.values())[0]['marketCap']
    print("{}, Name: {}, Ticker: {}, Industry: {}, Market Cap: {}".format(index, metadata['name'],
                                                                          metadata['ticker'],
                                                                          metadata['industry'],
                                                                          format_num(market_cap)))
    pretty_printer.pprint(metadata['longBusinessSummary'])
    print(d.summary_data.applymap(format_num))


def print_summary_for_name(name: str, data: List[ProcessedFinancialData]):
    x = [d for d in data if d.metadata['name'] == name][0]
    print_summary(x)


def scroll(data: List[ProcessedFinancialData], index=0):
    for i, d in enumerate(data[index:]):
        try:
            print_summary(d, i + index)
            on = input('Continue?')
            if on != '':
                break
        except:
            pass


def print_business_summary(data: List[ProcessedFinancialData]):
    pretty_printer = pp.PrettyPrinter()

    for d in data:
        pretty_printer.pprint(d.metadata['longBusinessSummary'])


def scroll_industry(data: List[ProcessedFinancialData]):
    pretty_printer = pp.PrettyPrinter()

    def inner_scroll_industry(industry_name: str, number: int):
        interested_industry = [c for c in data if c.metadata.get('industry') == industry_name]
        interested_industry_without_na = [i for i in interested_industry if i.summary_data.dropna().shape[0] != 0]
        descending_sort = sorted(interested_industry_without_na, key=lambda x: x.summary_data.loc['Total Revenue'][-1],
                                 reverse=True)
        intended_data = descending_sort[:number]
        print('Latest Years Data')
        print(compare_latest_years(intended_data))
        print()
        print('Averages Data')
        print(compare_averages(intended_data))
        print()
        for d in intended_data:
            metadata = d.metadata
            print("Name: {}, Ticker: {}".format(metadata['name'], metadata['ticker']))
            pretty_printer.pprint(metadata['longBusinessSummary'])
            print(d.summary_data.applymap(format_num))
            print()

    while True:
        next_industry = input('Industry?')
        top = input('Top How Many?')
        inner_scroll_industry(next_industry, int(top))

        on = input('Continue?')
        if on != '':
            break


def get_pe_data(data: List[ProcessedFinancialData]):
    results = []
    for d in data:
        try:
            market_cap = d.metadata.get('marketCap')
            price_to_book = market_cap / d.summary_data.loc['Stockholders Equity'][-1]
            average_roe = d.summary_data.loc['ROE'].mean()
            temp = {
                'name': d.metadata.get('name'),
                'trailingPE': d.metadata.get('trailingPE', math.nan),
                'forwardPE': d.metadata.get('forwardPE', math.nan),
                'marketCap': market_cap,
                'priceToBook': price_to_book,
                'averageROE': average_roe,
                'industry': d.metadata.get('industry'),
                'sector': d.metadata.get('sector')
            }
            results.append(temp)
        except:
            pass

    final_results = pd.DataFrame(results)
    final_results_without_financials = final_results[final_results.sector != 'Financials'].dropna(subset=['forwardPE'])
    return final_results_without_financials[final_results_without_financials.forwardPE > 0].sort_values(
        by=['forwardPE']).applymap(
        format_num)
