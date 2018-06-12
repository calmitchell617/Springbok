This code is dedicated to using pricing, and fundamental data from Quandl within Zipline.

Note: Everything that is quoted by single quotemarks... ' like this ' ... is a command to run in the command line.

Setup instructions:

1:  Make sure your environment is Python 3.5, and install the proper dependencies. I used Pyenv to accomplish this goal.
    Tutorial for setting up Pyenv on macOS:
    https://medium.com/@pimterry/setting-up-pyenv-on-os-x-with-homebrew-56c7541fd331

    Here is the summary of the commands you should run:

    If you already have homebrew installed (which you should)
    run: ' CFLAGS=“-I$(xcrun — show-sdk-path)/usr/include” '
    run: ' brew install pyenv '
    run: ' brew install readline '

    command line:
    Use pyenv to install python 3.5 ‘ pyenv install 3.5.5 ‘
    Run ‘pyenv versions’ to make sure you have the right python installed
    Run ‘pyenv global 3.5.5’ to make python 3.5.5 your currently running version
    Run ‘ eval "$(pyenv init -)” ‘

    Run ' python --version ' to make sure you are running Python 3.5.5
    At this point, we are running Python 3.5.5, using Pyenv. Great!

    Make sure pip is up to date: ‘ pip install --upgrade pip ‘
    pip install numpy
    pip install cython
    pip install -U setuptools

2:  We have installed the correct Python version, and Zipline's dependencies.. Now we need to install Zipline in
    such a way that we can easily modify / build it to our environment.

    I recommend cloning my Zipline fork on Github to a place where you want to keep the version of Zipline that you will
    modify in the future.

    command line:
    git clone https://github.com/calmitchell617/zipline.git
    git checkout -b WHATEVER-YOU-WANT-TO-CALL-YOUR-BRANCH
    pip install ROOT-DIRECTORY-OF-YOUR-GIT-CLONE

    Zipline should install, and we can now use this environment to do all kinds of fun stuff

3:  Download pricing and fundamental data from Quandl. Put these 2 files in the data_downloads folder.
    Pricing:        https://www.quandl.com/databases/SEP/documentation/batch-download
    Fundamentals:   https://www.quandl.com/databases/SF1/documentation/batch-download

4: Time to process the data!

    Run bundle_prep.py to process the pricing data into seperate OHLCV files for each ticker.
    (This step will take a little while. Should have written it in Go).

    Run reindex.py to finish processing pricing data

    Run drop_non_arq.py, this file strips away a lot of fluff that we won't use from the fundamental data.

    Run fundamentals_prep.py, this file puts the data for each alpha factor into a seperate folder.

5: Test to see if the thing works:
    Run basic_backtest.py, if it works, a CSV file should be written to the backtest_outputs folder. Hooray!