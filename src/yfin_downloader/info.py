import os
from datetime import datetime as dt
from yfin_downloader.downloader import download_stock_history, save_pickle
from yfin_downloader.utils import load_data
import yfinance as yf
import json
from yfin_downloader.utils import chunks, to_json
import asyncio
from concurrent.futures import ProcessPoolExecutor


def fetch(tickers, data_dir):
    errors = list()
    for ticker in tickers:
        try:
            filepath = '%s/%s_info.json' % (data_dir, ticker)
            if os.path.isfile(filepath):
                continue
            print('getting %s info' % ticker)
            stock = yf.Ticker(ticker)
            info = stock.info
            with open(filepath, 'w', encoding='utf8') as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
        except Exception as ex:
            print(ticker)
            print(ex)
            errors.append(ticker)
            continue
    return errors


async def async_fetch(tickers, data_dir):
    result = await loop.run_in_executor(executor, fetch, tickers, data_dir)
    return result


def main(ticker_lists, data_dir):
    tasks = []
    for tickers in ticker_lists:
        tasks.append(loop.create_task(async_fetch(tickers, data_dir)))

    done, _ = loop.run_until_complete(asyncio.wait(tasks))
    all_errors = list()
    for fut in done:
        all_errors = all_errors + fut.result()
    print(all_errors)
    to_json('errors_%s.json' % dt.today().date(), all_errors)


if __name__ == "__main__":

    lines = load_data("data/OTCBB.txt")

    tickers = []
    for line in lines[1:]:
        cols = line.strip().split("\t")
        ticker = cols[0].rstrip(".OB")
        tickers.append(ticker)

    total = len(tickers)
    count = 1
    working_dir = os.getcwd()
    dst_dir = '%s/data/info/%s' % (working_dir, str(dt.today().date()))
    try:
        if not os.path.isdir(dst_dir):
            os.mkdir(dst_dir)
    except OSError as ex:
        print(ex)
        assert False

    start_time = dt.now()

    ticker_lists = chunks(tickers, 10)
    loop = asyncio.get_event_loop()
    executor = ProcessPoolExecutor(max_workers=20)
    main(ticker_lists, dst_dir)

    """
    for ticker in tickers:
        try:
            print('%s of %s, getting %s' % (count, total, ticker))
            stock = yf.Ticker(ticker)
            info = stock.info
            with open('%s/%s_info.json' % (dst_dir, ticker), 'w', encoding='utf8') as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
            count += 1
        except Exception as ex:
            print(ex)
    """

    end_time = dt.now()
    print((end_time-start_time).total_seconds())
