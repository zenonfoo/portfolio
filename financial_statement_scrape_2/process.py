from functools import reduce
from typing import List
import math
from config import date_headers_to_filter
import pandas as pd
import os


def replace_character_with_space(table: List[List[str]], character: str) -> List[List[str]]:
    return [list(map(lambda x: x.replace(character, ''), row)) for row in table]


def delete_row(table: List[List[str]], deleteRow) -> List[List[str]]:
    return table[deleteRow:]


def remove_single_brackets(table: List[List[str]]) -> List[List[str]]:
    function = lambda x: x.strip() != ')' and x.strip() != '('
    return [list(filter(function, row)) for row in table]


def remove_blanks(table: List[List[str]]) -> List[List[str]]:
    return [list(filter(lambda x: x.strip() != '', row)) for row in table]


def remove_duplicate_string(table: List[List[str]]) -> List[List[str]]:
    results = []
    for row in table:
        temp_row = []
        for col in row:
            if col not in temp_row:
                temp_row.append(col)
            else:
                if all([not c.isalpha() for c in col]):
                    temp_row.append(col)
        results.append(temp_row)
    return results


def remove_empty_lines_or_single_column(table: List[List[str]]) -> List[List[str]]:
    return [row for row in table if len(row) != 0 and len(row) != 1]


def remove_columns_larger_than_4(table: List[List[str]]) -> List[List[str]]:
    return [row for row in table if len(row) <= 4]


def fulfil_brackets(table: List[List[str]]) -> List[List[str]]:
    def helper(x: str):
        if '(' in x and ')' not in x:
            return x + ')'
        elif ')' in x and '(' not in x:
            return '(' + x
        else: return x
    return [list(map(helper, row)) for row in table]


def match_column_length(table: List[List[str]]) -> List[List[str]]:
    date_headers = table[0]
    data_to_use = table[1:]
    lengths_of_row = {len(x) for x in data_to_use}
    length_to_use = max(lengths_of_row)
    new_data = []
    for data in data_to_use:
        if len(data) == length_to_use - 1:
            data.insert(0, '')
        new_data.append(data)
    new_data.insert(0, date_headers)
    return new_data


def convert_to_num_if_possible(x: str):
    try:
        commaSeparate = x.split(',')
        combinedNumber = reduce(lambda x, y: x + y, commaSeparate)
        if x.strip()[0] == '(' and x.strip()[-1] == ')':
            return -float(combinedNumber[1:-1])
        elif x.strip() == '-' or x.strip() == '—':
            return 0
        else:
            tempStore = float(combinedNumber)
            if math.isnan(tempStore):
                return 0
            else:
                return tempStore
    except:
        return x


def convert_str_num_to_int_num(table: List[List[str]]) -> List[List[str]]:
    return [list(map(convert_to_num_if_possible, row)) for row in table]


def remove_non_number_financial_value(table: List[List[str]]) -> List[List[str]]:
    new_table = [table[0]]
    for row in table[1:]:
        values = list(filter(lambda x: type(x) is not str, row[1:]))
        new_row = [row[0]] + values
        new_table.append(new_row)
    return new_table


def remove_wrong_date_header(table: List[List[str]]) -> List[List[str]]:
    filtered_date_header = []

    for header in table[0]:
        check = list(map(lambda x: x not in str(header), date_headers_to_filter))
        if all(check):
            filtered_date_header.append(header)

    table[0] = filtered_date_header

    return table


def convert_to_key_word_format(table: List[List[str]]) -> List[List[str]]:
    new_table = []
    for row in table:
        if type(row[0]) == str:
            temp_row = row
            temp_row[0] = row[0].lower().replace(' ', '-')
            new_table.append(temp_row)
        else:
            new_table.append(temp_row)
    return new_table


def generate_key(keys, key, appender):
    while key in keys:
        new_key = generate_key(keys, key + ' - ' + appender, appender)
        return new_key
    return key


def convert_statement_to_dict(table: List[List[str]]) -> dict:
    dates = table[0]
    new_table = table[1:]
    new_dict = {}
    for row in new_table:
        data = {}
        for date, column in zip(dates, row[1:]):
            data.update({date: column})
        try:
            key = generate_key(new_dict.keys(), row[0].strip(), '_')
            new_dict[key] = data
        except:
            raise Exception("Error")
    return new_dict


def convert_all_keys_to_str(data: dict):
    new_dict = {}
    for key in data.keys():
        dict_key = str(key)
        new_dict[dict_key.strip()] = data[key]
    return new_dict


def convert_header_to_str_date(table: List[List[str]]) -> List[List[str]]:
    try:
        helper = lambda x: str(x).split('.')[0]
        temp_table_0 = list(map(helper, table[0]))
        final_table_0 = []
        if len(temp_table_0) != len(table[1]) - 1:
            temp_table_0 = temp_table_0[1:]

        for col in temp_table_0:
            if ',' in col:
                final_table_0.append(col.split(',')[1].replace(' ', ''))
            elif ' ' in col:
                final_table_0.append(col.split(' ')[1].replace(' ', ''))
            else:
                final_table_0.append(col)
        table[0] = final_table_0
        return table
    except:
        raise Exception("Error with convert_header_to_str_date: " + str(table[0]))


def process_table(table: List[List[str]]) -> List[List[str]]:
    return reduce(lambda x, y: y(x),
                  [table,
                   lambda x: replace_character_with_space(x, '\xa0'),
                   lambda x: replace_character_with_space(x, '\n'),
                   lambda x: replace_character_with_space(x, '\x97'),
                   lambda x: replace_character_with_space(x, '%'),
                   lambda x: replace_character_with_space(x, '\u200b'),
                   lambda x: replace_character_with_space(x, '$'),
                   remove_blanks,
                   remove_duplicate_string,  # Mainly for date that has month in row above
                   remove_empty_lines_or_single_column,
                   remove_single_brackets,
                   fulfil_brackets,
                   remove_columns_larger_than_4,
                   remove_wrong_date_header,
                   convert_str_num_to_int_num,
                   remove_non_number_financial_value,
                   match_column_length,
                   convert_header_to_str_date,
                   convert_statement_to_dict,
                   convert_all_keys_to_str])


def process_all_financial_statements(data: dict) -> dict:
    final_data = {'income_statement': process_table(data['income_statement']),
                  'balance_sheet': process_table(data['balance_sheet']), 'cash_flow': process_table(data['cash_flow'])}
    return final_data


def save_to_csv(data: List[dict], name: str) -> None:
    for statements in data:
        for key in statements.keys():
            statement = pd.DataFrame(statements[key]).transpose()
            year = statement.columns[0]
            directory = os.getcwd() + '/statements/' + name + '/' + year
            if not os.path.exists(directory):
                os.makedirs(directory)
            statement.to_csv(directory + '/' + key)
