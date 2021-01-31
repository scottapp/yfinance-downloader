import os
from datetime import datetime as dt
import concurrent.futures
from yfin_downloader.utils import load_data, to_json
import asyncio
from concurrent.futures import ProcessPoolExecutor
from ratemate import RateLimit

import requests
import json
import time
import codecs

import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='log/main_download_otc_security_detail.log', filemode='w', format=FORMAT)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def fetch_data(dst_dir, ticker):
    try:
        waited_time = rate_limit.wait()
        url = 'https://backend.otcmarkets.com/otcapi/company/profile/full/%s?symbol=%s' % (ticker, ticker)
        r = requests.get(url)
        assert r.status_code == 200, 'error status code, %s, %s' % (r.status_code, ticker)
        with codecs.open('%s/%s.json' % (dst_dir, ticker), 'w', encoding='utf8') as f:
            r.encoding = 'utf8'
            json_data = json.loads(r.text)
            f.write(json.dumps(json_data, ensure_ascii=False, indent=2))
    except Exception as ex:
        print(ticker)
        print(ex)
        logging.error(ex)
    return r.status_code


def fetch(dst_dir, tickers):
    errors = list()
    for ticker in tickers:
        time.sleep(0.5)
        try:
            logging.info('downloading %s' % ticker)
            url = 'https://backend.otcmarkets.com/otcapi/company/profile/full/%s?symbol=%s' % (ticker, ticker)
            r = requests.get(url)
            assert r.status_code == 200, 'error status code, %s, %s' % (r.status_code, ticker)
            with codecs.open('%s/%s.json' % (dst_dir, ticker), 'w', encoding='utf8') as f:
                r.encoding = 'utf8'
                json_data = json.loads(r.text)
                f.write(json.dumps(json_data, ensure_ascii=False, indent=2))
        except Exception as ex:
            print(ticker)
            print(ex)
            logging.error(ex)
            errors.append(ticker)
            continue
    return errors


async def async_fetch(dst_dir, tickers):
    result = await loop.run_in_executor(executor, fetch, dst_dir, tickers)
    return result


def run_async(dst_dir, ticker_lists):
    tasks = []
    for tickers in ticker_lists:
        tasks.append(loop.create_task(async_fetch(dst_dir, tickers)))

    done, _ = loop.run_until_complete(asyncio.wait(tasks))
    all_errors = list()
    for fut in done:
        all_errors = all_errors + fut.result()
    print(all_errors)
    to_json('errors_download_otc_detail_%s.json' % dt.today().date(), all_errors)


if __name__ == "__main__":
    try:
        cur_dir = os.getcwd()
        data_dir = '%s/data' % cur_dir
        assert os.path.isdir(data_dir), 'error data dir, %s' % data_dir

        today_date = dt.today().date()
        dst_dir = '%s/info/%s' % (data_dir, today_date)
        try:
            if not os.path.isdir(dst_dir):
                os.mkdir(dst_dir)
        except OSError as ex:
            logging.error(ex)
            assert False

        lines = load_data("data/OTCBB-2021-01-29.txt")

        tickers = []
        for line in lines[1:]:
            cols = line.strip().split("\t")
            ticker = cols[0].rstrip(".OB")
            tickers.append(ticker)
        ticker_lists = chunks(tickers, 10)

        loop = asyncio.get_event_loop()

        """
        executor = ProcessPoolExecutor(max_workers=10)
        run_async(dst_dir, ticker_lists)
        """

        rate_limit = RateLimit(max_count=60, per=60)  # 2 requests per 5 seconds

        # We can use a with statement to ensure threads are cleaned up promptly
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Start the load operations and mark each future with its URL
            future_to_ticker = {executor.submit(fetch_data, dst_dir, ticker): ticker for ticker in tickers}
            for completed in concurrent.futures.as_completed(future_to_ticker):
                ticker = future_to_ticker[completed]
                try:
                    status_code = completed.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (ticker, exc))
                else:
                    print('%s, %s' % (ticker, status_code))
                    if status_code == 429:
                        assert False, 'too many requests, stopping now'

    except Exception as ex:
        logging.error(ex)
