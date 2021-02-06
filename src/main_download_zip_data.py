import os
from datetime import datetime as dt
from yfin_downloader.cloud import download_blob
import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='log/main_download_zip_data.log', filemode='w', format=FORMAT)


def init():
    project_id = os.getenv('PROJECT_ID', None)
    assert project_id, 'error project id'

    key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', None)
    assert key, 'error key'

    return project_id


if __name__ == '__main__':
    try:
        project_id = init()
        bucket = '%s-test' % project_id
        zip_filename = '%s-yfin-data.zip' % str(dt.today().date())
        download_blob(bucket, zip_filename, './data/zips/%s' % zip_filename)
        print('done')
    except Exception as ex:
        logging.error(ex)
