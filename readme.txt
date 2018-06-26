## Using Fundamental Data For Backtests Within Zipline

It is common to see questions related to using external, fundamental data for backtests within Zipline.
I have developed an easy way of implementing data from Sharadar’s SF1 (fundamentals) and SEP (pricing) datasets.
These are very popular datasets because of their relative robustness, in relation to their low price.

Others have written about this topic, such as Jonathan Larkin on Zipline Github issue #911:
https://github.com/quantopian/zipline/issues/911
and Peter Harrington on his AlphaCompiler blog: http://alphacompiler.com/blog/6/

I tried both of these methods, and found that neither of them worked for my particular use case.
It is worth noting that my code borrows heavily from Jonathan Larkin’s implementation of dispatching custom loaders when creating a data pipeline, with a special shout out to Scott Sanderson for helping me alter Zipline to make the run_algorithm() function accept dataframe loaders.

Because this method uses Pandas Data Frames to load all data into the data pipeline (using the DataFrameLoader class https://github.com/quantopian/zipline/blob/master/zipline/pipeline/loaders/frame.py), you can only load data which will fit in your computer’s RAM. My next improvement will be implementing the Blaze loader in order to increase loading speed, and do away with this annoying limitation.

I will now go over all of the files within this repo by explaining what they do, what may break in the future, and how you can change the file to fit your individual needs. If you don’t care about any of that, go to https://github.com/calmitchell617/Springbok and check out the readme. It has succinct setup instructions without any extra prose.

The first thing you need to do is set up the proper Python Environment. To summarize, you need to install Python 3.5, numpy, pandas, cython, matplotlib, and setuptools, before you can install Zipline.

The official Zipline docs recommends using Conda to set up this environment, but it seems that Conda sometimes doesn’t install the very latest version of Zipline.
I use pip and Pyenv to set up my environment, here are my step by step instructions for setting up shop on macOS.

(PS: Head over to https://pythonprogramming.net/zipline-local-install-python-programming-for-finance/ if you want setup instructions for Windows or Linux).

Step 1: Install Python 3.5.5 using Pyenv

Assuming you already have Homebrew, using the command line, navigate to the directory that you downloaded my air repo to, and run:

run: CFLAGS="-I$(xcrun — show-sdk-path)/usr/include"
run: brew install pyenv
run: brew install readline
Install python 3.5.5: pyenv install 3.5.5
Run: pyenv versions
Make sure 3.5.5 is listed
Run: pyenv local 3.5.5
Makes it so Python 3.5.5 is associated with this directory
Run: eval "$(pyenv init -)”
Run: python --version
Check to make sure you are running Python 3.5.5 .. If so, great!

If you get stuck, here is a tutorial for setting up Pyenv on macOS:
https://medium.com/@pimterry/setting-up-pyenv-on-os-x-with-homebrew-56c7541fd331

Step 2: Install Zipline (and a few other) dependencies using pip

Run: pip install --upgrade pip
Makes sure pip is up to date
Run: pip install numpy
Run: pip install pandas
Run: pip install cython
Run: pip install -U setuptools

Step 3: Install my modified version of Zipline

Navigate to the directory that you want my version of zipline to download to, and run on the command line:

git clone https://github.com/calmitchell617/zipline.git
pip install (copy and paste the path of where you installed my zipline repo here)

Zipline should now install, and we can now use this environment to do all kinds of fun stuff

Step 4: Download and process data from Quandl / Sharadar

Run mkdirs.py to setup the proper folder structure
Download pricing and fundamental data from Quandl. Unzip, and put these 2 files in the data_downloads folder.
Pricing:        https://www.quandl.com/databases/SEP/documentation/batch-download
Fundamentals:   https://www.quandl.com/databases/SF1/documentation/batch-download
process_data.py (will take an hour + to process all of the data. Will print “Done!” When it’s done.

Step 5: Ingest the data bundle

You should ingest all pricing data into what’s known as a data bundle.
To do this, we will take our CSV files, which have been processed into the correct OHLCV format, and run the “zipline ingest” command from the command line.
To get successfully run this command, we will have to make a few changes to Zipline itself, however.

The .zipline file folder is hidden by default, so you need to alter your computer to reveal hidden files and directories.
In macOS Sierra and later, this is quite easy. While in Finder, press “Command + Shift + . “, and hidden files and folders will be revealed.
In windows, just google “windows reveal hidden files” and your windows version.
If you’re running linux, you probably already know how to do it.
Now find your .zipline folder, which is under your user directory.
For example, on mac, this is under MacintoshHD -> Users -> the username you are currently using.
Open “extension.py” to modify it.
Change the start_session variable to match the date which your pricing data starts on
Change the end_session variable to match the date that your pricing dataends on.
Change the first parameter in the register() function to: ' sharadar-pricing '
Make sure the first parameter of the csvdir_equites() function is ' ['daily'] '
Make the second parameter of the csvdir_equites() function the full directory of your pricing folder...
For example, my directory is ' /Users/calmitchell/s/springbok-shared/processed_data/pricing/ '
This folder should contain one other folder named ' daily '.
Make sure you are running Python 3.5.5 with Zipline installed properly, step 1 above ^^^.
Run: zipline ingest -b 'sharadar-pricing'
This will take a few minutes. Make sure to check to see if any fatal errors occurred, and also check the .zipline directory for a new folder called sharadar-pricing.
Open the folder within that folder, and if its not empty, that means you are in business!

Step 6: Run basic_backtest.py to ensure everything is working

At this point, you have ingested pricing data, processed fundamental data into a known directory, and run a backtest using the data.
Check out the comments and structure of basic_backtest.py to further your understanding of how to work with Zipline.

Happy alpha hunting!
