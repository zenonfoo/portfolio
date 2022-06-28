import pandas as pd
from load_yahooquery import load_all_data
from calc_yahooquery import calc_many
from utils import combine_print, get_pe_data, print_summary_for_name

x = load_all_data()

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 1000)

data = [x for x in load_all_data() if x is not None]
data_with_pe = [x for x in data if x.metadata.get('trailingPE')]
calc_data = calc_many(data)
calc_data_with_metadata = [c for c in calc_data if
                           type(c.metadata) == dict and c.summary_data.dropna().shape[0] != 0 and
                           c.summary_data.dropna().shape[1] != 0]
us_companies = [c for c in calc_data_with_metadata if
                c.financial_data.income_statement.loc['currency Code'][0] == 'USD' and c.metadata.get(
                    'country') == 'United States']
us_pe_data = get_pe_data(calc_data)


companies_roe_larger_20 = [c for c in calc_data_with_metadata if
                           c.summary_data.loc['ROE'].replace('-', 0).mean() > 0.2 and
                           c.summary_data.loc['Stockholders Equity'].replace('-', 0).sum() > 0 and
                           c.summary_data.loc['Net Income Common Stockholders'].replace('-', 0).sum() > 0]

# Industries
industries = pd.Series([c.metadata.get('industry') for c in us_companies if type(c.metadata) == dict])
print(industries.value_counts())

# Top 10 of x in industry
industry = 'Auto Parts'
interested_industry = [c for c in us_companies if c.metadata.get('industry') == industry]
interested_industry_without_na = [i for i in interested_industry if i.summary_data.dropna().shape[0] != 0]
descending_sort = sorted(interested_industry_without_na, key=lambda x: x.summary_data.loc['Total Revenue'][-1],
                         reverse=True)
combined_to_print = combine_print(descending_sort[:5])
print(combined_to_print)

######################################################################
from utils import scroll, compare_latest_years, compare_averages, print_business_summary, scroll_industry

scroll(companies_roe_larger_20[::-1])

intended_data = descending_sort[:4]
compare_averages(intended_data)
compare_latest_years(intended_data)
combine_print(intended_data)
print_business_summary(intended_data)

# pe_data[pe_data.industry != 'Asset Management'].sort_values(by=['trailingPE']).dropna().head(50).applymap(format_num)
# final_results[final_results.industry != 'Asset Management'].sort_values(by=['trailingPE']).dropna().applymap(format_num)