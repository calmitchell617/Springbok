import pandas as pd
from collections import OrderedDict
import numpy as np

fundamentals_directory = 'processed_data/fundamentals'

earnings_df = pd.read_csv('{}/netinc.csv'.format(fundamentals_directory), index_col=0)
revenue_df = pd.read_csv('{}/revenue.csv'.format(fundamentals_directory), index_col=0)
growth_df = pd.DataFrame(index=earnings_df.index, columns=earnings_df.columns)

tickers = OrderedDict()

for ticker in earnings_df.columns:
    tickers[ticker] = {'earnings': None, 'changed': 0}

iterator = earnings_df.iterrows()

for i, row in iterator:

    for ticker in tickers:

        if pd.isnull(row[ticker]):
            continue

        else:
            if tickers[ticker]['earnings'] is None:
                tickers[ticker]['earnings'] = row[ticker]
                tickers[ticker]['changed'] = 1

            if tickers[ticker]['changed'] == 1 and tickers[ticker]['earnings'] != row[ticker]:
                tickers[ticker]['changed'] = 2
                tickers[ticker]['earnings'] = row[ticker]

            if revenue_df.loc[i, ticker] != 0 and tickers[ticker]['changed'] == 2 and tickers[ticker]['earnings'] != row[ticker]:
                growth_df.loc[i, ticker] = (row[ticker] - tickers[ticker]['earnings']) / revenue_df.loc[i, ticker]
                tickers[ticker]['earnings'] = row[ticker]
                print(growth_df.loc[i, ticker])


    print(growth_df)
    if i == "2013-09-20 00:00:00+00:00":
        break

growth_df.to_csv('{}/earnings_growth.csv'.format(fundamentals_directory))


# for row in earnings df
# for each column
# if there is a value
# check if there was a previous value
# if there was, calculate the ratio of this value / the previous value, subtract 1, write to that cell
# if there wasn't set the value