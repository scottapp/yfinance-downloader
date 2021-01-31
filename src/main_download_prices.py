import os
from datetime import datetime as dt
from yfin_downloader.downloader import download_stock_history
from yfin_downloader.utils import load_data, to_json, zipdir, save_pickle
import asyncio
from concurrent.futures import ProcessPoolExecutor
import zipfile
from yfin_downloader.cloud import upload_blob
from google.cloud import pubsub_v1

import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='log/main_download_prices.log', filemode='w', format=FORMAT)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def fetch(tickers, data_dir, period):
    errors = list()
    for ticker in tickers:
        try:
            logging.info('downloading %s' % ticker)
            df = download_stock_history(ticker, period)
            if not df.empty:
                save_pickle(df, '%s/%s_prices.pkl' % (data_dir, ticker))
        except Exception as ex:
            logging.error(ex)
            errors.append(ticker)
            continue
    return errors


async def async_fetch(tickers, data_dir, period):
    result = await loop.run_in_executor(executor, fetch, tickers, data_dir, period)
    return result


def run_async(ticker_lists, data_dir, period):
    tasks = []
    for tickers in ticker_lists:
        tasks.append(loop.create_task(async_fetch(tickers, data_dir, period)))

    done, _ = loop.run_until_complete(asyncio.wait(tasks))
    all_errors = list()
    for fut in done:
        all_errors = all_errors + fut.result()
    print(all_errors)
    to_json('errors_%s.json' % dt.today().date(), all_errors)


def main():
    project_id = os.getenv('PROJECT_ID', None)
    assert project_id, 'error project id'

    key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', None)
    assert key, 'error key'

    lines = load_data("data/OTCBB-2021-01-29.txt")

    tickers = []
    for line in lines[1:]:
        cols = line.strip().split("\t")
        ticker = cols[0].rstrip(".OB")
        tickers.append(ticker)

    tickers = tickers[0:100]

    total = len(tickers)
    working_dir = os.getcwd()
    dst_dir = '%s/data/%s' % (working_dir, str(dt.today().date()))
    try:
        if not os.path.isdir(dst_dir):
            os.mkdir(dst_dir)
    except OSError as ex:
        logging.error(ex)
        assert False

    start_time = dt.now()

    ticker_lists = chunks(tickers, 10)
    run_async(ticker_lists, dst_dir, '6mo')

    end_time = dt.now()
    logging.info((end_time - start_time).total_seconds())

    # zip the data directory
    zip_filename = '%s-yfin-data.zip' % str(dt.today().date())
    zipf = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)
    zipdir(dst_dir, zipf)
    zipf.close()

    # upload zip to google cloud
    bucket = '%s-test' % project_id
    upload_blob(bucket, '%s/%s' % (working_dir, zip_filename), zip_filename)
    logging.info("upload completed")

    """
    publisher = pubsub_v1.PublisherClient()
    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_id}`
    topic_path = publisher.topic_path(project_id, "daily_yahoo_download")
    
    data = "OK:%s" % zip_filename
    data = data.encode("utf-8")
    future = publisher.publish(topic_path, data)
    logging.info(future.result())
    """


"""
def extract(tar_path, target_path):
    try:
        tar = tarfile.open(tar_path, "r:gz")
        file_names = tar.getnames()
        for file_name in file_names:
            tar.extract(file_name, target_path)
        tar.close()
    except Exception as ex:
        print(ex)
"""


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        executor = ProcessPoolExecutor(max_workers=20)
        main()
    except Exception as ex:
        logging.error(ex)
