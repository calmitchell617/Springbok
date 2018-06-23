import helper_functions
from zipline.data import bundles
from zipline.pipeline import Pipeline
from zipline.pipeline.data import USEquityPricing, Column, DataSet
from zipline.pipeline.loaders.frame import DataFrameLoader
from zipline.utils.run_algo import load_extensions
from zipline import run_algorithm
from zipline.api import (
    attach_pipeline,
    pipeline_output,
    order_target,
    order_target_percent,
    get_open_orders,
    record
)

import os
import datetime as dt

import pandas as pd
import matplotlib
matplotlib.use('TkAgg')  # This forces matplotlib to use TkAgg as a backend
import matplotlib.pyplot as plt


class MyDataSet(DataSet):  # This is where we create columns to put in our pipeline
    cap = Column(dtype=float)
    pe1 = Column(dtype=float)
    de = Column(dtype=float)
    eg = Column(dtype=float)

def prepare_data(bundle_data):

    # Specify where our CSV files live
    fundamentals_directory = 'processed_data/fundamentals/'
    pricing_directory = 'processed_data/pricing/daily/'

    # The following two variables are ordered dicts that contain the name of every security in the pricing,
    # and fundamental directories, respectfully.
    pricing_assets = helper_functions.get_pricing_securities(pricing_directory)
    fundamental_assets, dates = helper_functions.get_dates(fundamentals_directory)

    # Securities that are in both pricing_assets, and fundamental_assets
    tickers = helper_functions.get_tickers_in_both(pricing_assets, fundamental_assets)

    date_stamps = helper_functions.convert_to_date_stamps(dates)

    pe1_df = pd.read_csv('{}{}.csv'.format(fundamentals_directory, 'pe1'), usecols=tickers)
    de_df = pd.read_csv('{}{}.csv'.format(fundamentals_directory, 'de'), usecols=tickers)
    eg_df = pd.read_csv('{}{}.csv'.format(fundamentals_directory, 'earnings_growth'), usecols=tickers)
    cap_df = pd.read_csv('{}{}.csv'.format(fundamentals_directory, 'marketcap'), usecols=tickers)

    assets = bundle_data.asset_finder.lookup_symbols([ticker for ticker in pe1_df.columns], as_of_date=None)
    sids = pd.Int64Index([asset.sid for asset in assets])

    pe1_frame, pe1_frame.index, pe1_frame.columns = pe1_df, date_stamps, sids
    de_frame, de_frame.index, de_frame.columns = de_df, date_stamps, sids
    eg_frame, eg_frame.index, eg_frame.columns = eg_df, date_stamps, sids
    cap_frame, cap_frame.index, cap_frame.columns = cap_df, date_stamps, sids

    return {  # Every column of data needs its own loader
        MyDataSet.pe1: DataFrameLoader(MyDataSet.pe1, pe1_frame),
        MyDataSet.de: DataFrameLoader(MyDataSet.de, de_frame),
        MyDataSet.eg: DataFrameLoader(MyDataSet.eg, eg_frame),
        MyDataSet.cap: DataFrameLoader(MyDataSet.cap, cap_frame),
    }

def make_pipeline():

    return Pipeline(
        columns={
            'price': USEquityPricing.close.latest,
            'pe1': MyDataSet.pe1.latest,
            'de': MyDataSet.de.latest,
            'eg': MyDataSet.eg.latest,
            'cap': MyDataSet.cap.latest,
        },
        screen=USEquityPricing.close.latest.notnull() &
               MyDataSet.de.latest.notnull() &
               MyDataSet.pe1.latest.notnull() &
               MyDataSet.eg.latest.notnull() &
               MyDataSet.cap.latest.notnull()
    )

def initialize(context):

    context.longs_portfolio = {}
    context.shorts_portfolio = {}

    attach_pipeline(
        make_pipeline(),
        'data_pipe'
    )

def before_trading_start(context, data): 
    """
    function is run every day before market opens
    """
    context.output = pipeline_output('data_pipe')

    context.cap_plays = context.output.sort_values(['cap'])[-4000:]  # take top 4000 stocks by market cap for liquidity

    context.longs = helper_functions.get_longs(context.cap_plays)

    context.shorts = helper_functions.get_shorts(context.cap_plays)

    record(open_orders=str(get_open_orders()))


def handle_data(context, data):
    """
    Run every day, at market open.
    """

    longs_to_remove = []

    for asset in context.longs_portfolio:  # search portfolio for positions to close out
        if asset not in context.longs.index:
            longs_to_remove.append(asset)
            order_target(asset, 0)

    for asset in context.longs.index:  # search context.longs for stocks to add to portfolio
        if asset not in context.longs_portfolio:
            context.longs_portfolio[asset] = True
            order_target_percent(asset, .005)

    for key in longs_to_remove:
        context.longs_portfolio.pop(key)

    shorts_to_remove = []

    for asset in context.shorts_portfolio:  # search portfolio for positions to close out
        if asset not in context.shorts.index:
            shorts_to_remove.append(asset)
            order_target(asset, 0)

    for asset in context.shorts.index:  # search context.shorts for stocks to add to portfolio
        if asset not in context.shorts_portfolio:
            context.shorts_portfolio[asset] = True
            order_target_percent(asset, -0.005)

    for key in shorts_to_remove:
        context.shorts_portfolio.pop(key)

def analyze(context, perf):
    """
    Helper function that runs once the backtest is finished
    """
    perf.to_csv('backtest_outputs/backtest_on_{}.csv'.format(str(dt.datetime.now())))

    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    perf.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('portfolio value in $')
    plt.legend(loc=0)
    plt.show()

if __name__ == "__main__":

    load_extensions(
        default=True,
        extensions=[],
        strict=True,
        environ=os.environ,
    )

    bundle_data = bundles.load('sharadar-pricing')  # This is a bundle made from Sharadar SEP data

    loaders = prepare_data(bundle_data)

    run_algorithm(
        bundle='sharadar-pricing',
        before_trading_start=before_trading_start,
        start=pd.Timestamp('2018-04-01', tz='utc'),
        end=pd.Timestamp('2018-04-20', tz='utc'),
        initialize=initialize,
        analyze=analyze,
        capital_base=100000,
        handle_data=handle_data,
        loaders=loaders
    )
