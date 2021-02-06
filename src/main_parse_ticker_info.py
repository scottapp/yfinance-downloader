from yfin_downloader.utils import load_data
from datetime import datetime as dt
import os
import json


"""
class Details(object):
    def __init__(self):
        self.outstandingShares = None
        self.publicFloat = None
"""


def parse_ticker_info():
    lines = load_data("data/OTCBB-2021-01-29.txt")
    tickers = []
    for line in lines[1:]:
        cols = line.strip().split("\t")
        ticker = cols[0].rstrip(".OB")
        tickers.append(ticker)

    working_dir = os.getcwd()
    data_dir = '%s/data/info/2021-01-31' % working_dir

    infos = dict()
    errors = dict()
    for ticker in tickers:
        try:
            file_path = '%s/%s.json' % (data_dir, ticker)
            if not os.path.isfile(file_path):
                errors[ticker] = 'missing data file'
                continue

            print(ticker)
            with open(file_path, 'r', encoding='utf8') as f:
                details = dict()
                data = json.loads(f.read())
                security_data = data.get('securities', [])
                assert security_data, 'missing security data'
                security_data = security_data[0]

                details['publicFloat'] = security_data.get('publicFloat', None)
                details['unrestrictedShares'] = security_data.get('unrestrictedShares', None)
                details['publicFloatAsOfDate'] = security_data.get('publicFloatAsOfDate', 0)
                details['unrestrictedSharesAsOfDate'] = security_data.get('unrestrictedSharesAsOfDate', 0)
                infos[ticker] = details

        except Exception as ex:
            print(ticker)
            print(ex)
            errors[ticker] = str(ex)
            continue

    today_date = dt.today().date()
    with open('float_data_%s.json' % today_date, 'w', encoding='utf8') as f:
        f.write(json.dumps(infos, indent=2, ensure_ascii=False))
    print(errors)


def purge_empty_file(dir_path):
    files_to_delete = []
    for file in os.listdir(dir_path):
        if file.endswith('.json'):
            statinfo = os.stat('%s/%s' % (dir_path, file))
            if statinfo.st_size == 0:
                print('%s, %s' % (file, statinfo.st_size))
                files_to_delete.append(file)
    print(len(files_to_delete))
    for file in files_to_delete:
        os.remove('%s/%s' % (dir_path, file))


if __name__ == "__main__":

    try:
        #dir_path = 'data/info/2021-01-31'
        #purge_empty_file(dir_path)
        parse_ticker_info()
    except Exception as ex:
        print(ex)
