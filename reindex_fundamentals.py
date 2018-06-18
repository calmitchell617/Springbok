import os
from collections import OrderedDict
import pandas as pd
from zipline.utils.calendars import get_calendar

preprocessed_directory = 'processed_data/sparse_fundamentals'
last_directory = 'processed_data/done'

data_list = []

data = OrderedDict()

for root, dirs, files in os.walk(preprocessed_directory):  # Lets get all of our tickers
    for file in files:
        if file.startswith('earnings_growth'):
            data_list.append(file[:-4])

data_list.sort()

for point in data_list:
    data[point] = True

for point in data_list:  # we need to reindex the files to deal with missing data (we will forward fill)

    df = pd.read_csv('{}/{}.csv'.format(preprocessed_directory, point), index_col=0)
    length = len(df.index) - 1
    start_date = df.index[0]
    end_date = df.index[length]

    actual_sessions = df.index.tolist()

    stamps = [str(pd.Timestamp(session, tz='UTC', offset='C')) for session in actual_sessions]

    df.index = stamps

    sessions = get_calendar('NYSE').sessions_in_range(start_date, end_date).tolist()



    for i in range(len(sessions)):
        sessions[i] = str(sessions[i])

    print(df.index.tolist())
    print(sessions)


    try:
        df = df.reindex(sessions)
        df = df.fillna(method='pad')
    except ValueError:
        print(point)
        continue

    df.to_csv('{}/{}.csv'.format(last_directory, point))
