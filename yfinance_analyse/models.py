import pandas as pd
from typing import List


class FinancialData:

    def __init__(self, income_statement: pd.DataFrame, balance_sheet: pd.DataFrame, cash_flow: pd.DataFrame):
        self.income_statement = income_statement
        self.balance_sheet = balance_sheet
        self.cash_flow = cash_flow


class UnprocessedFinancialData:
    def __init__(self, financial_data: List[FinancialData], metadata: dict):
        self.financial_data = financial_data
        self.metadata = metadata


class ProcessedFinancialData:
    def __init__(self, financial_data: FinancialData, summary_data: pd.DataFrame, metadata: dict):
        self.financial_data = financial_data
        self.summary_data = summary_data
        self.metadata = metadata
