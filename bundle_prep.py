import os
import pandas as pd
import csv

downloads_directory = 'data_downloads'
processed_directory = 'processed_data/pricing/preprocessed'

tickers = {}

for root, dirs, files in os.walk(downloads_directory): # Lets get all of our tickers
    for file in files:
        if file.startswith('SHARADAR_SEP'):
            pricing_df = pd.read_csv('{}/{}'.format(downloads_directory, file))

            for ticker in pricing_df['ticker']:
                if ticker not in tickers:
                    tickers[ticker] = True

            for ticker in tickers:
                with open('{}/{}.csv'.format(processed_directory, ticker), 'w') as processed_file:
                    writer = csv.writer(processed_file)
                    writer.writerow(['date', 'open', 'high', 'low', 'close', 'volume', 'dividend', 'split'])

            iterator = pricing_df.iterrows()
            next(iterator)
            for i, row in iterator:
                with open('{}/{}.csv'.format(processed_directory, row['ticker']), 'a') as ticker_file:
                    ticker_writer = csv.writer(ticker_file)
                    ticker_writer.writerow(
                        [
                            pd.Timestamp(row['date'], tz='UTC'),
                            row['open'],
                            row['high'],
                            row['low'],
                            row['close'],
                            row['volume'],
                            row['dividends'],
                            1.0,
                        ]
                    )
