from itertools import product
from typing import List, Tuple

# Things to filter from financial statements
date_headers_to_filter = ['(in millions, except share data)', 'June 30', 'June30',
                          '(In thousands, except per share amounts)', '(In thousands, except share amounts)',
                          '(In thousands)', '(In millions, except per share data)',
                          '(In millions, except par value data)', '(In millions)']

# Financial statement headers
tags = ['span', 'b', 'font', 'p']
income_statement = ['consolidated statements of income',
                    'consolidated statements of operations',
                    'consolidated statements of (loss) income',
                    'consolidated statements of income (loss)',
                    'consolidated statement of operations',
                    'consolidated statements of operations',
                    'consolidated income statements',
                    'income statements',
                    'consolidated statements of comprehensive income',
                    'consolidated statements of comprehensive\nincome',
                    'consolidated statements of operations and comprehensive loss',
                    'consolidated statements of operations and comprehensive income',
                    'consolidated statements of operations and comprehensive income (loss)',
                    'consolidated statements of income (operations)']
balance_sheet = ['consolidated balance sheets',
                 'consolidated balance sheet',
                 'balance sheet']
cash_flow = ['consolidated statement of cash flows',
             'consolidated statements of cash flows',
             'cash flows statement']


def get_list_of_possible_statement_headers() -> List[Tuple[str, str, str, str]]:
    return list(product(*[tags, income_statement, balance_sheet, cash_flow]))
