import pandas as pd

from zipline.data.bundles import register
from zipline.data.bundles.csvdir import csvdir_equities

start_session = pd.Timestamp('2013-01-02', tz='UTC')
end_session = pd.Timestamp('2018-07-03', tz='UTC')

register(
    'sharadar-pricing',
    csvdir_equities(
        ['daily'],
        '/Users/calmitchell/s/Springbok-filled/processed_data/pricing',
    ),
    calendar_name='NYSE',  # US equities
    start_session=start_session,
    end_session=end_session
)

