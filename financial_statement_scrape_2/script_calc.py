import os
import pandas as pd
from typing import List

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class Calc:

    def __init__(self, thousand_wrapper=lambda x: x):
        self.thousand_wrapper = thousand_wrapper
        self.income_statement = 'income_statement'
        self.balance_sheet = 'balance_sheet'
        self.cash_flow = 'cash_flow'
        self.divide = lambda x, y: x / y

    @staticmethod
    def load_data(stock_folder_name: str):
        try:
            os.remove("{}/statements/{}/.DS_STORE".format(ROOT_DIR, stock_folder_name))
        except:
            print("No DS_STORE to remove")
        path = "{}/statements/{}".format(ROOT_DIR, stock_folder_name)
        years = [x for x in os.listdir(path) if x != "script.py"]
        try:
            years.remove('__pycache__')
        except:
            pass

        results = {}
        for year in years:
            current_path = path + '/' + year
            statements = os.listdir(current_path)
            results[year] = {}
            for statement in statements:
                data = pd.read_csv(current_path + '/' + statement, index_col=0)
                results[year][statement] = data

        return results

    @staticmethod
    # Latest data being first and oldest being last
    def cagr(data: List[float]):
        growth = data[0] / data[-1]
        return (growth ** (1 / len(data))) - 1

    @staticmethod
    def cagr_df(data: pd.DataFrame):
        indices = data.index
        print("Compound Annual Growth Rate for {} years".format(data.shape[1]))
        for index in indices:
            result = Calc.cagr(data.loc[index].values)
            print("{}: {}".format(index, round(result, 3)))

    def get_line(self, data: dict, statement: str, line: str, display_name: str):
        result = None
        for i, year in enumerate(sorted(data.keys(), reverse=True)):
            try:
                intended_statement: pd.DataFrame = data[year][statement]
                name = next(filter(lambda x: line in x, intended_statement.index.fillna('')))
                statement_series = intended_statement.loc[name]
                statement_series.name = display_name
                statement_frame = pd.DataFrame(statement_series).transpose()
                if i == 0:
                    result = statement_frame
                else:
                    result = result.combine_first(statement_frame)
            except:
                print('get_line error: {}'.format(year))
        return self.thousand_wrapper(result.transpose().sort_index(ascending=False).transpose())

    def get_and_operate_on_lines(self, data: dict, statement, lines: List[str], display_name: str, add=True):
        result = None
        for i, year in enumerate(sorted(data.keys(), reverse=True)):
            try:
                intended_statement: pd.DataFrame = data[year][statement].copy()
                line_names = []
                for line in lines:
                    line_names += list(filter(lambda x: line in x, intended_statement.index.fillna('')))
                temp_result = None
                for j, line_name in enumerate(line_names):
                    line_value = intended_statement.loc[line_name]
                    if j == 0:
                        temp_result = line_value
                    else:
                        if add:
                            temp_result += line_value
                        else:
                            temp_result -= line_value
                temp_result.name = display_name
                temp_result_frame = pd.DataFrame(temp_result).transpose()
            except:
                print('get_and_operate_on_lines error: {}'.format(year))
            if i == 0:
                result = temp_result_frame
            else:
                result = result.combine_first(temp_result_frame)

        return self.thousand_wrapper(result.transpose().sort_index(ascending=False).transpose())

    @staticmethod
    def operate_on_results(data: pd.DataFrame, first, second, func, resulting_name):
        result = func(data.loc[first], data.loc[second])
        result.name = resulting_name
        return pd.concat([data, pd.DataFrame(result).transpose()])

    @staticmethod
    def operate_on_results_onto_new_df(data: pd.DataFrame, new_df, first, second, func, resulting_name):
        result = func(data.loc[first], data.loc[second])
        result.name = resulting_name
        return pd.concat([new_df, pd.DataFrame(result).transpose()])
