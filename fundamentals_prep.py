import pandas as pd
from collections import OrderedDict
import csv

downloads_directory = 'data_downloads'
processed_directory = 'processed_data/fundamentals'
io_directory = 'io_files'

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

main_df = pd.read_csv('{}/all_arq.csv'.format(io_directory))
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

    write_df.to_csv('{}/{}.csv'.format(processed_directory, column))
