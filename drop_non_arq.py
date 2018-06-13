import os
import csv

downloads_directory = 'data_downloads'
processed_directory = 'io_files'

rows_to_drop = []

for root, dirs, files in os.walk(downloads_directory): # Lets get all of our tickers
    for file in files:
        if file.startswith('SHARADAR_SF1'):
            with open('{}/{}'.format(downloads_directory, file), 'r') as read_file:
                with open('{}/all_arq.csv'.format(processed_directory), 'w') as write_file:
                    reader = csv.reader(read_file)
                    writer = csv.writer(write_file)
                    first_line_gone = False
                    for row in reader:
                        if first_line_gone is True:
                            if row[1] == 'ARQ':
                                writer.writerow(row)
                        else:
                            writer.writerow(row)
                            first_line_gone = True