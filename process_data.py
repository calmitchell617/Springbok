def bundle_prep():

    downloads_directory = 'data_downloads'
    directory = 'processed_data/pricing/daily'

    tickers = OrderedDict()

    for root, dirs, files in os.walk(downloads_directory):  # Lets get all of our tickers
        for file in files:
            if file.startswith('SHARADAR_SEP'):
                pricing_df = pd.read_csv('{}/{}'.format(downloads_directory, file))

                for ticker in pricing_df['ticker']:
                    if ticker not in tickers:
                        tickers[ticker] = True

                for ticker in tickers:
                    with open('{}/{}.csv'.format(directory, ticker), 'w') as processed_file:
                        writer = csv.writer(processed_file)
                        writer.writerow(['date', 'open', 'high', 'low', 'close', 'volume'])

                iterator = pricing_df.iterrows()
                next(iterator)
                for i, row in iterator:
                    with open('{}/{}.csv'.format(directory, row['ticker']), 'a') as ticker_file:
                        ticker_writer = csv.writer(ticker_file)
                        ticker_writer.writerow(
                            [
                                row['date'],
                                row['open'],
                                row['high'],
                                row['low'],
                                row['close'],
                                row['volume']

                            ]
                        )

    for ticker in tickers:  # we need to reindex the files to deal with missing data (we will forward fill)

        df = pd.read_csv('{}/{}.csv'.format(directory, ticker), index_col='date')
        length = len(df.index) - 1
        start_date = df.index[0]
        end_date = df.index[length]

        sessions = get_calendar('NYSE').sessions_in_range(start_date, end_date).tolist()

        for i in range(len(sessions)):
            sessions[i] = str(sessions[i])

        try:
            df = df.reindex(sessions, method='pad')
            os.remove('{}/{}.csv'.format(directory, ticker))
            df.to_csv('{}/{}.csv'.format(directory, ticker))
        except ValueError:
            print(ticker)
            os.remove('{}/{}.csv'.format(directory, ticker))
            continue

    print("Bundle prep is finished.")


def fundamentals_prep():

    downloads_directory = 'data_downloads'
    directory = 'processed_data/fundamentals'

    for root, dirs, files in os.walk(downloads_directory):  # Lets get all of our tickers
        for file in files:
            if file.startswith('SHARADAR_SF1'):
                with open('{}/{}'.format(downloads_directory, file), 'r') as read_file:
                    with open('{}/all_arq.csv'.format(directory), 'w') as write_file:
                        reader = csv.reader(read_file)
                        writer = csv.writer(write_file)
                        first_line_gone = False
                        for row in reader:
                            if first_line_gone is True:
                                if row[1] == 'ARQ':
                                    writer.writerow(row)
                            else:
                                writer.writerow(row)
                                first_line_gone = True

    desired_data = [
        'accoci',
        'assets',
        'assetsc',
        'assetsnc',
        'bvps',
        'capex',
        'cashneq',
        'cashnequsd',
        'cor',
        'consolinc',
        'currentratio',
        'de',
        'debt',
        'debtc',
        'debtnc',
        'debtusd',
        'deferredrev',
        'depamor',
        'deposits',
        'divyield',
        'dps',
        'ebit',
        'ebitda',
        'ebitdamargin',
        'ebitdausd',
        'ebitusd',
        'ebt',
        'eps',
        'epsdil',
        'epsusd',
        'equity',
        'equityusd',
        'ev',
        'evebit',
        'evebitda',
        'fcf',
        'fcfps',
        'fxusd',
        'gp',
        'grossmargin',
        'intangibles',
        'intexp',
        'invcap',
        'invcapavg',
        'inventory',
        'investments',
        'investmentsc',
        'investmentsnc',
        'liabilities',
        'liabilitiesc',
        'liabilitiesnc',
        'marketcap',
        'ncf',
        'ncfbus',
        'ncfcommon',
        'ncfdebt',
        'ncfdiv',
        'ncff',
        'ncfi',
        'ncfinv',
        'ncfo',
        'ncfx',
        'netinc',
        'netinccmn',
        'netinccmnusd',
        'netincdis',
        'netincnci',
        'netmargin',
        'opex',
        'opinc',
        'payables',
        'payoutratio',
        'pb',
        'pe',
        'pe1',
        'ppnenet',
        'prefdivis',
        'price',
        'ps',
        'ps1',
        'receivables',
        'retearn',
        'revenue',
        'revenueusd',
        'rnd',
        'sbcomp',
        'sgna',
        'sharefactor',
        'sharesbas',
        'shareswa',
        'shareswadil',
        'sps',
        'tangibles',
        'taxassets',
        'taxexp',
        'taxliabilities',
        'tbvps',
        'workingcapital'
    ]

    # get all dates and tickers

    main_df = pd.read_csv('{}/all_arq.csv'.format(directory))
    date_stamps = sorted(set(main_df['datekey'].tolist()))
    for i in range(len(date_stamps)):
        date_stamps[i] = pd.Timestamp(date_stamps[i], tz='UTC')
    tickers = sorted(set(main_df['ticker'].tolist()))

    for column in desired_data:
        read_df = main_df[['datekey', 'ticker', column]]
        write_df = pd.DataFrame(index=date_stamps, columns=tickers)

        iterator = read_df.iterrows()
        for i, row in iterator:
            write_df[row['ticker']].loc[row['datekey']] = row[column]

        write_df.to_csv('{}/{}.csv'.format(directory, column))

    try:
        os.remove('{}/all_arq.csv'.format(directory))
    except OSError:
        pass

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

                    if tickers[ticker]['cur_earnings'] is None:  # first value
                        tickers[ticker]['cur_earnings'] = row[ticker]
                        continue

                    tickers[ticker]['prev_earnings'] = tickers[ticker]['cur_earnings']
                    tickers[ticker]['cur_earnings'] = row[ticker]

                    rev = revenue_df.loc[i, ticker]

                    if rev != 0:
                        tickers[ticker]['rev_growth'] = (
                                    (tickers[ticker]['cur_earnings'] - tickers[ticker]['prev_earnings']) / rev)
                        new_df.ix[i, ticker] = tickers[ticker]['rev_growth']
                else:
                    new_df.ix[i, ticker] = tickers[ticker]['rev_growth']

    new_df.to_csv('{}/earnings_growth.csv'.format(fundamentals_directory))

    directory = 'processed_data/fundamentals'

    data_list = []

    data = OrderedDict()

    for root, dirs, files in os.walk(directory):  # Lets get all of our tickers
        for file in files:
            if file.endswith('csv'):
                data_list.append(file[:-4])

    data_list.sort()

    for point in data_list:
        data[point] = True

    for point in data_list:  # we need to reindex the files to deal with missing data (we will forward fill)

        df = pd.read_csv('{}/{}.csv'.format(directory, point), index_col=0)
        length = len(df.index) - 1
        start_date = df.index[0]
        end_date = df.index[length]

        actual_sessions = df.index

        stamps = [str(pd.Timestamp(session, tz='UTC', offset='C')) for session in actual_sessions]

        df.index = stamps

        sessions = get_calendar('NYSE').sessions_in_range(start_date, end_date).tolist()

        for i in range(len(sessions)):
            sessions[i] = str(sessions[i])

        try:
            df = df.reindex(sessions)
            df = df.fillna(method='pad')
            os.remove('{}/{}.csv'.format(directory, point))
        except ValueError:
            print(point)
            continue

        df.to_csv('{}/{}.csv'.format(directory, point))

    print("Fundamentals prep is finished.")


if __name__ == "__main__":

    import multiprocessing
    import os
    import pandas as pd
    import csv
    from collections import OrderedDict
    from zipline.utils.calendars import get_calendar

    # creating processes
    p1 = multiprocessing.Process(target=bundle_prep)
    p2 = multiprocessing.Process(target=fundamentals_prep)

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    # both processes finished
    print("Done!")
