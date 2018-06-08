Setup instructions:

1:  Make sure your environment is Python 3.5, and install the proper dependencies. I used Pyenv to accomplish this goal.
    Tutorial for setting up Pyenv on macOS:
    https://medium.com/@pimterry/setting-up-pyenv-on-os-x-with-homebrew-56c7541fd331

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

3:  Get the skeleton of our project by git cloning ' https://github.com/calmitchell617/springbok-shared.git '
    Download pricing and fundamental data from Quandl. Put these 2 files in the data_downloads folder.
    Pricing:        https://www.quandl.com/databases/SEP/documentation/batch-download
    Fundamentals:   https://www.quandl.com/databases/SF1/documentation/batch-download

    Run bundle_prep.py to process the pricing data into a the correct format. The data will populate in the
    processed_data folder. (This step will take a little while. Should have written it in Go).

AAMC is the first problem child with missing data. 