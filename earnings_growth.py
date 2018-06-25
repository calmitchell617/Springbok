import pandas as pd
from collections import OrderedDict

fundamentals_directory = 'processed_data/fundamentals'

earnings_df = pd.read_csv('{}/netinc.csv'.format(fundamentals_directory), index_col=0)
revenue_df = pd.read_csv('{}/revenue.csv'.format(fundamentals_directory), index_col=0)
growth_df = earnings_df
new_df = pd.DataFrame(index=earnings_df.index, columns=earnings_df.columns)

tickers = OrderedDict()

for ticker in earnings_df.columns:
    tickers[ticker] = {'prev_earnings': None, 'cur_earnings': None, 'rev_growth': None}

iterator = growth_df.iterrows()

for i, row in iterator:

    for ticker in tickers:
        if not pd.isnull(row[ticker]):
            if row[ticker] != tickers[ticker]['cur_earnings']:

                if tickers[ticker]['cur_earnings'] is None: # first value
                    tickers[ticker]['cur_earnings'] = row[ticker]
                    continue

                tickers[ticker]['prev_earnings'] = tickers[ticker]['cur_earnings']
                tickers[ticker]['cur_earnings'] = row[ticker]

                rev = revenue_df.loc[i, ticker]

                if rev != 0:
                    tickers[ticker]['rev_growth'] = ((tickers[ticker]['cur_earnings'] - tickers[ticker]['prev_earnings']) / rev)
                    new_df.ix[i, ticker] = tickers[ticker]['rev_growth']
            else:
                new_df.ix[i, ticker] = tickers[ticker]['rev_growth']




new_df.to_csv('{}/earnings_growth.csv'.format(fundamentals_directory))
