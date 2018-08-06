from utilities import helper_functions as helper_functions

from zipline.data import bundles
from zipline.pipeline import Pipeline, CustomFactor
from zipline.pipeline.data import USEquityPricing, Column, DataSet
from zipline.pipeline.factors import Returns
from zipline.pipeline.loaders.frame import DataFrameLoader
from zipline.utils.run_algo import load_extensions
from zipline import run_algorithm
from zipline.api import (
    attach_pipeline,
    pipeline_output,
    get_open_orders,
    symbol,
    set_max_leverage,
    order_target_percent,
    record
)

import os
import datetime as dt

import pandas as pd
import matplotlib
matplotlib.use('TkAgg')  # This forces MatPlotLib to use TkAgg as a backend
import matplotlib.pyplot as plt

def prepare_data(bundle_data):
    """
    This function takes a data bundle and matches fundamental data points to the correct asset objects.
    :param bundle_data: The data bundle that you ingested from SEP
    :return: A dictionary of loaders to be used within a data pipeline, and a DataSet class with the correct columns
    """

    """
    Enter the name of the data points you wish to use in the backtest here. The names need to match the name of the
    appropriate CSV file found in processed_data/fundamentals
    """
    data_points = ['marketcap']

    # Specify where our CSV files live
    fundamentals_directory = 'processed_data/fundamentals/'
    pricing_directory = 'processed_data/pricing/daily/'

    # pricing_assets is an ordered dict that contains the name of every security in the pricing directory
    pricing_assets = helper_functions.get_pricing_securities(pricing_directory)

    """
    fundamental_assets is an ordered dict that contains the name of every security in the fundamentals directory
    dates is a list of dates that the fundamentals directory is indexed by
    """
    fundamental_assets, dates = helper_functions.get_dates(fundamentals_directory)

    # Securities that are in both pricing_assets, and fundamental_assets
    tickers = helper_functions.get_tickers_in_both(pricing_assets, fundamental_assets)

    date_stamps = helper_functions.convert_to_date_stamps(dates)

    data_frames = {}

    for data in data_points:
        # creates a dataframe for each data point, puts it in the data_frames dict
        data_frames[data] = helper_functions.make_frame(data, fundamentals_directory, tickers)

    for data_frame in data_frames:
        """
        assets variable becomes a list of Asset objects, sids becomes a list of SID objects corresponding to the correct
        assets.
        """
        assets = bundle_data.asset_finder.lookup_symbols([ticker for ticker in data_frames[data_frame].columns],
                                                         as_of_date=None)
        sids = pd.Int64Index([asset.sid for asset in assets])
        break


    class MyDataSet(DataSet):
        """
        We need to create an attribute for each needed data point within MyDataSet, before __new__() runs...
        This is so MyDataSet converts the Column types into BoundColumn types.
        """
        for point in data_points:
            locals()[point] = Column(dtype=float)

    """
    We are finally ready to create a dictionary of data frame loaders, with corresponding BoundColumn attributes
    within our MyDataSet class. 
    """
    data_frame_loaders = {}

    for data_frame in data_frames:
        """
        Reindexes the dataframe indexes with date_stamps instead of dates, and replaces the column names (which are
        currently strings) with SIDS.
        """
        data_frames[data_frame].index, data_frames[data_frame].columns = date_stamps, sids

    for attr in data_frames:
        """
        Fills data_frame_loaders with key value pairs of: MyDataSet.attribute_name: DataFrameLoader(attribute_name
        """
        data_frame_loaders[getattr(MyDataSet, attr)] = DataFrameLoader(getattr(MyDataSet, attr), data_frames[attr])

    return data_frame_loaders, MyDataSet

def make_pipeline():

    yearly_returns = Returns(window_length=252)

    monthly_returns = Returns(window_length=21)

    lagged_returns = yearly_returns - monthly_returns

    return Pipeline(
        columns={
            'lagged_returns': lagged_returns,
            'marketcap': MyDataSet.marketcap.latest,
        },
        screen=lagged_returns.notnull() &
               MyDataSet.marketcap.latest.notnull() &
               MyDataSet.marketcap.latest.top(500)
    )

def initialize(context):
    """
    Function runs once, at the start of the backtest. You must attach_pipeline() here.
    :param context: A common namespace to keep variables in
    :return:
    """


    attach_pipeline(
        make_pipeline(),
        'data_pipe'
    )

def before_trading_start(context, data):
    """
    Runs once a day, before trading start
    :param context: The common namespace
    :param data:
    :return:
    """


def handle_data(context, data):
    """
    Runs every day, at market open
    :param context: Common namespace
    :param data:
    :return:
    """

    order_target_percent(symbol('AAPL'), 1)

def analyze(context, perf):
    """
    Helper function that runs at the end of backtest for analysis
    :param context: Common namespace
    :param perf: The data which shows how the backtest performed
    :return:
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

    bundle = bundles.load('sharadar-pricing')  # This is a bundle made from Sharadar SEP data

    data_frame_loaders, MyDataSet = prepare_data(bundle)

    print('Made it to run_algorithm')

    run_algorithm(
        bundle='sharadar-pricing',
        before_trading_start=before_trading_start,
        start=pd.Timestamp('2017-01-02', tz='utc'),
        end=pd.Timestamp('2018-04-20', tz='utc'),
        initialize=initialize,
        analyze=analyze,
        capital_base=10000,
        handle_data=handle_data,
        data_frame_loaders=data_frame_loaders
    )
