import os
from datetime import datetime as dt
from yfin_downloader.cloud import download_blob
from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='log/main_download_zip_data.log', filemode='w', format=FORMAT)


def callback(message):
    logging.info(f"Received {message}.")
    message.ack()
    bucket = '%s-test' % project_id
    #zip_filename = '%s-yfin-data.zip' % str(dt.today().date())
    assert str(message).startswith("OK:")
    zip_filename = str(message).split(':')[1]
    download_blob(bucket, zip_filename, './data/zips/%s' % zip_filename)


def init():
    project_id = os.getenv('PROJECT_ID', None)
    assert project_id, 'error project id'

    key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', None)
    assert key, 'error key'

    return project_id


def run_subscriber(project_id, subscription_id):
    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            #streaming_pull_future.result(timeout=5.0)
            streaming_pull_future.result()
        except TimeoutError:
            logging.error(TimeoutError)
            streaming_pull_future.cancel()


if __name__ == '__main__':
    try:
        project_id = init()
        #run_subscriber(project_id, "")
        bucket = '%s-test' % project_id
        zip_filename = '%s-yfin-data.zip' % str(dt.today().date())
        download_blob(bucket, zip_filename, './data/zips/%s' % zip_filename)
        print('done')
    except Exception as ex:
        logging.error(ex)
