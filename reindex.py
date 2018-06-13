import os
from collections import OrderedDict
import pandas as pd
from zipline.utils.calendars import get_calendar

preprocessed_directory = 'processed_data/pricing/preprocessed'
last_directory = 'processed_data/pricing/daily'

tickers_list = []

tickers = OrderedDict()

for root, dirs, files in os.walk(preprocessed_directory):  # Lets get all of our tickers
    for file in files:
        if file.endswith('csv'):
            tickers_list.append(file[:-4])

tickers_list.sort()

for ticker in tickers_list:
    tickers[ticker] = True

for ticker in tickers_list:  # we need to reindex the files to deal with missing data (we will forward fill)

    df = pd.read_csv('{}/{}.csv'.format(preprocessed_directory, ticker), index_col='date')
    length = len(df.index) - 1
    start_date = df.index[0]
    end_date = df.index[length]

    sessions = get_calendar('NYSE').sessions_in_range(start_date, end_date).tolist()

    for i in range(len(sessions)):
        sessions[i] = str(sessions[i])


    try:
        df = df.reindex(sessions, method='pad')
    except ValueError:
        print(ticker)
        continue

    df.to_csv('{}/{}.csv'.format(last_directory, ticker))
