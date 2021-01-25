from yfin_downloader.utils import load_data
import datetime
from datetime import datetime as dt
import os
import json
import codecs


def parse_ticker_info():
    lines = load_data("data/OTCBB.txt")
    tickers = []
    for line in lines[1:]:
        cols = line.strip().split("\t")
        ticker = cols[0].rstrip(".OB")
        tickers.append(ticker)

    working_dir = os.getcwd()
    data_dir = '%s/data/info/2021-01-16' % working_dir

    float_shares = dict()
    for ticker in tickers:
        try:
            print(ticker)
            file_path = '%s/%s_info.json' % (data_dir, ticker)
            with open(file_path, 'r', encoding='utf8') as f:
                ticker_data = json.loads(f.read())
                float_shares[ticker] = ticker_data['floatShares']
        except Exception as ex:
            print(ex)
            continue

    with open('float_data.json', 'w', encoding='utf8') as f:
        f.write(json.dumps(float_shares, indent=2, ensure_ascii=False))


if __name__ == "__main__":

    try:
        parse_ticker_info()
    except Exception as ex:
        print(ex)
