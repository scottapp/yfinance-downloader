import os
import datetime
from datetime import datetime as dt
from yfin_downloader.utils import load_pickle
from yfin_downloader.utils import load_data
import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='log/main_extract_data_range.log', filemode='w', format=FORMAT)


def extract_latest_month_data(trade_date):
    lines = load_data("data/OTCBB-2021-01-29.txt")
    tickers = []
    for line in lines[1:]:
        cols = line.strip().split("\t")
        ticker = cols[0].rstrip(".OB")
        tickers.append(ticker)

    today = dt.today()
    range_start = today - datetime.timedelta(days=180)

    total = len(tickers)
    count = 1
    working_dir = os.getcwd()

    dst_dir = '%s/data/%s-2' % (working_dir, trade_date)
    try:
        if not os.path.isdir(dst_dir):
            os.mkdir(dst_dir)
    except OSError as ex:
        logging.error(ex)
        assert False

    for ticker in tickers:
        try:
            df = load_pickle('data/%s/%s_prices.pkl' % (trade_date, ticker))
            target_range = df.loc[range_start:today]
            target_range.to_pickle("%s/%s.pkl" % (dst_dir, ticker))
            print('%s/%s saved %s' % (count, total, ticker))
            count += 1
        except Exception as ex:
            logging.error(ex)
            continue


def extract_twse_data(trade_date, ticker):
    try:
        df = load_pickle('data/twse/%s/%s_prices.pkl' % (trade_date, ticker))
        print(df)
    except Exception as ex:
        logging.error(ex)


if __name__ == "__main__":
    try:
        today_date = str(dt.today().date())
        #extract_latest_month_data(today_date)
        extract_twse_data(today_date, '9925.TW')
    except Exception as ex:
        logging.error(ex)


