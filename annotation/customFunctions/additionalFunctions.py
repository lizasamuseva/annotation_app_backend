import os
from datetime import datetime, timedelta


#Creates file with path_to_file and opens with mode append, if it doesn't exist.
#Otherwise, truncate the file.
def open_output_file(path_to_file):
    if os.path.exists(path_to_file):
        file = open(path_to_file, 'a')
        file.truncate(0)
    else:
        file = open(path_to_file, 'a')
    return file






#Converting date format to serial number according to txt ADInstrument documentation
#https://www.adinstruments.com/support/knowledge-base/how-do-i-set-specific-start-time-and-date-imported-text-file
# def convert_date_to_serial_number(date):
#     temp = datetime(1899, 12, 31)
#     delta = date - temp
#     return float(delta.days) + (float(delta.seconds) / 86400)

