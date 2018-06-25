It is common to see questions related to using external, fundamental data for backtests within Zipline. I have developed an easy way of implementing data from Sharadar’s SF1 (fundamentals) and SEP (pricing) datasets. These are very popular datasets because of their relative robustness, in relation to their low price. 

Others have written about this topic, such as Jonathan Larkin on Zipline Github issue #911: https://github.com/quantopian/zipline/issues/911 , and Peter Harrington on his AlphaCompiler blog: http://alphacompiler.com/blog/6/ . 

I tried both of these methods, and found that neither of them worked for my particular use case. It is worth noting that my code borrows heavily from Jonathan Larkin’s implementation of dispatching custom loaders when creating a data pipeline, with a special shout out to Scott Sanderson for helping me alter Zipline to make the run_algorithm() function accept dataframe loaders. 

Because this method uses Pandas Data Frames to load all data into the data pipeline (using the DataFrameLoader class https://github.com/quantopian/zipline/blob/master/zipline/pipeline/loaders/frame.py), you can only load data which will fit in your computer’s RAM. My next improvement will be implementing the Blaze loader in order to increase loading speed, and do away with this annoying limitation. 

I will now go over all of the files within this repo by explaining what they do, what may break in the future, and how you can change the file to fit your individual needs. If you don’t care about any of that, go to https://github.com/calmitchell617/Springbok and check out the readme. It has succinct setup instructions without any extra prose. 

The first thing you need to do is set up the proper Python Environment. To summarize, you need to install Python 3.5, numpy, pandas, cython, matplotlib, setuptools, BEFORE you can install Zipline. 

The official Zipline docs recommends using Conda to set up this environment, but it seems that Conda sometimes doesn’t install the very latest version of Zipline. I use pip and Pyenv to set up my environment, here are my step by step instructions for setting up shop on macOS. 

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
Ingest the data bundle 


To be continued….