from zipline.pipeline.data import Column, BoundColumn
from collections import OrderedDict
import os
import pandas as pd


def get_pricing_securities(pricing_directory):
    """
    Builds a list of all securities, represented by a csv file, in the pricing_directory folder
    :param pricing_directory:
    :return: return list, an ordered dict of security names
    """

    return_dict = OrderedDict()

    for root, dirs, files in os.walk(pricing_directory):
        for file in files:
            if file.endswith('.csv'):
                return_dict[file[:-4]] = True

    return return_dict


def get_dates(fundamentals_directory):
    """
    Looks at first csv file in fundamentals_directory, build list of securities and dates
    :param fundamentals_directory:
    :return: return_dict: an ordered dict with the name of every security as a key, and True as the value
             dates: a list of all dates, as datestamps, that are in the csv index.
    """
    return_dict = OrderedDict()
    for root, dirs, files in os.walk(fundamentals_directory):
        for file in files:
            print(file)
        for file in files:
            if file.endswith('.csv'):
                fundamental_tickers_df = pd.read_csv('{}{}'.format(fundamentals_directory, file), index_col=0)

                for ticker in fundamental_tickers_df.columns:
                    return_dict[ticker] = True

                dates = fundamental_tickers_df.index.tolist()

                return return_dict, dates


def get_tickers_in_both(pricing_assets, fundamental_assets):
    """
    Compares tickers from pricing assets, and fundamental assets, and filter out tickers not in both
    :param pricing_assets:
    :param fundamental_assets:
    :return: list
    """
    tickers_in_both = []

    for ticker in pricing_assets:
        if ticker in fundamental_assets:
            tickers_in_both.append(ticker)

    return tickers_in_both


def convert_to_date_stamps(dates):
    """
    Given a list of dates, convert to tz aware datestamps, returns as list.
    :param dates:
    :return: list
    """
    datestamps = []

    for date in dates:
        tz_aware_date = pd.Timestamp(date, tz='utc')
        datestamps.append(tz_aware_date)

    return datestamps


def make_frame(data_name, fundamentals_directory, tickers):
    return pd.read_csv('{}{}.csv'.format(fundamentals_directory, data_name), usecols=tickers)

def reformat_frame(df, date_stamps, sids):
    df.index, df.columns = date_stamps, sids

def set_dataset_columns(data_points, cls):
    for point in data_points:
        setattr(cls, point, Column(dtype=float))
    return cls
