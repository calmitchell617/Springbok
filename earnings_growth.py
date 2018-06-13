import pandas as pd
from collections import OrderedDict
import numpy as np

fundamentals_directory = 'processed_data/fundamentals'

earnings_df = pd.read_csv('{}/netinc.csv'.format(fundamentals_directory), index_col=0)
revenue_df = pd.read_csv('{}/revenue.csv'.format(fundamentals_directory), index_col=0)
growth_df = pd.DataFrame(index=earnings_df.index, columns=earnings_df.columns)

tickers = OrderedDict()

for ticker in earnings_df.columns:
    tickers[ticker] = None

print(tickers)

iterator = earnings_df.iterrows()
for i, row in iterator:
    for ticker in tickers:
        if pd.isnull(row[ticker]):
            continue
        else:
            if tickers[ticker] is None:
                tickers[ticker] = row[ticker]
            else:
                growth_df.loc[i][ticker] = (row[ticker] - tickers[ticker]) / revenue_df.loc[i][ticker]
                tickers[ticker] = row[ticker]


growth_df.to_csv('{}/earnings_growth.csv'.format(fundamentals_directory))


# for row in earnings df
# for each column
# if there is a value
# check if there was a previous value
# if there was, calculate the ratio of this value / the previous value, subtract 1, write to that cell
# if there wasn't set the value