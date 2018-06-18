from zipline.data import bundles
from zipline.pipeline import Pipeline
from zipline.pipeline.data import USEquityPricing, Column, DataSet
from zipline.pipeline.engine import SimplePipelineEngine
from zipline.pipeline.filters import StaticAssets
from zipline.pipeline.loaders import USEquityPricingLoader
from zipline.pipeline.loaders.frame import DataFrameLoader
from zipline.utils.calendars import get_calendar
from zipline.pipeline.factors import SimpleMovingAverage
from zipline.api import order_target, record, symbol

import os

import datetime as dt
from collections import OrderedDict
import pandas as pd
from zipline.utils.run_algo import load_extensions

load_extensions(
    default=True,
    extensions=[],
    strict=True,
    environ=os.environ,
)

bundle_data = bundles.load('sharadar-pricing')

fundamentals_directory = '/Users/calmitchell/s/springbok-shared/processed_data/fundamentals/'
pricing_directory = '/Users/calmitchell/s/springbok-shared/processed_data/pricing/daily/'

pricing_assets = OrderedDict()
fundamental_assets = OrderedDict()

tickers = []
        
for root, dirs, files in os.walk(pricing_directory):
    for file in files:
        if file.endswith('.csv'):
            pricing_assets[file[:-4]] = True
            
for root, dirs, files in os.walk(fundamentals_directory): 
    for file in files:
        if file.endswith('.csv'):
            fundamental_tickers_df = pd.read_csv('{}{}'.format(fundamentals_directory, file), index_col=0)

            for ticker in fundamental_tickers_df.columns:
                fundamental_assets[ticker] = True
                
            dates = fundamental_tickers_df.index.tolist()
            
            break

for ticker in pricing_assets:
    if ticker in fundamental_assets:
        tickers.append(ticker)

datestamps = []

for date in dates:
    newer_date = pd.Timestamp(date, tz='utc')
    datestamps.append(newer_date)


class MyDataSet(DataSet): # This is where we create columns to put in our pipeline
    pe1 = Column(dtype=float)
    de = Column(dtype=float)
    eg = Column(dtype=float)

pe1_df = pd.read_csv('{}{}.csv'.format(fundamentals_directory, 'pe1'), usecols=tickers)
de_df = pd.read_csv('{}{}.csv'.format(fundamentals_directory, 'de'), usecols=tickers)
eg_df = pd.read_csv('{}{}.csv'.format(fundamentals_directory, 'earnings_growth'), usecols=tickers)


assets = bundle_data.asset_finder.lookup_symbols([ticker for ticker in pe1_df.columns], as_of_date=None)
sids = pd.Int64Index([asset.sid for asset in assets])

pe1_frame, pe1_frame.index, pe1_frame.columns  = pe1_df, datestamps, sids
de_frame, de_frame.index, de_frame.columns  = de_df, datestamps, sids
eg_frame, eg_frame.index, eg_frame.columns  = eg_df, datestamps, sids

loaders = { # Every column of data needs its own loader
    MyDataSet.pe1: DataFrameLoader(MyDataSet.pe1, pe1_frame),
    MyDataSet.de: DataFrameLoader(MyDataSet.de, de_frame),
    MyDataSet.eg: DataFrameLoader(MyDataSet.eg, eg_frame),
}

pipeline_loader = USEquityPricingLoader( # a default loader for us equity pricing
    bundle_data.equity_daily_bar_reader,
    bundle_data.adjustment_reader,
)

def make_pipeline():
    """
    Data from a pipeline is available to your algorithm in before_trading_start(),
    and handle_data(), as long as you attach the pipeline in initialize().
    """
    return Pipeline(
        columns={
            'price': USEquityPricing.close.latest,
            'pe1': MyDataSet.pe1.latest,
            'de': MyDataSet.de.latest,
            'eg': MyDataSet.eg.latest
        },
        screen = StaticAssets(assets) &
                 USEquityPricing.close.latest.notnull() &
                 MyDataSet.de.latest.notnull() &
                 MyDataSet.pe1.latest.notnull() &
                 MyDataSet.eg.latest.notnull()
    )

from zipline.data import bundles
from zipline.api import symbol, order, record, schedule_function, attach_pipeline, pipeline_output
from zipline import run_algorithm
from zipline.utils.run_algo import load_extensions
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

portfolio = {}

def initialize(context):
    attach_pipeline(
        make_pipeline(),
        'data_pipe'
    )
def before_trading_start(context, data): 
    """
    function is run every day before market opens
    """


    context.output = pipeline_output('data_pipe')
    context.pe1 = context.output.sort_values(['pe1'])[-100:]
    context.eg = context.pe1.sort_values(['eg'])[-33:]
    context.de = context.eg.sort_values(['de'])[:10]


def handle_data(context, data):
    """
    Run every day, at market open.
    """

    keys_to_remove = []
    assets_held = []
    assets_bought = []
    assets_sold = []

    for asset in portfolio:
        if asset not in context.de.index: # remove key from portfolio
            keys_to_remove.append(asset)
            order(asset, -portfolio[asset]['shares'])
            assets_sold.append(asset)
        else:
            assets_held.append(asset)

    for key in keys_to_remove:
        portfolio.pop(key)

    for asset in context.de.index:
        if asset not in portfolio:
            order(asset, 10)
            portfolio[asset] = {'shares': 10}
            assets_bought.append(asset)

    record(assets_held=str(assets_held))
    record(assets_bought=str(assets_bought))
    record(assets_sold=str(assets_sold))


    record(portfolio=str(portfolio))


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


# Alright, let's start the show!
# You need to run this iPython cell twice for the matplotlib graph to show up. No idea why.

# I do not have access to SPY or any other benchmark to compare our algorithm right now,
# but I'm working on it.


start = pd.Timestamp('2014-09-01', tz='utc')
end = pd.Timestamp('2018-04-20', tz='utc')

print('made it to run algorithm')

run_algorithm(
    bundle='sharadar-pricing',
    before_trading_start=before_trading_start, 
    start = start, 
    end=end, 
    initialize=initialize, 
    analyze=analyze,
    capital_base=10000, 
    handle_data=handle_data,
    loaders=loaders
)
