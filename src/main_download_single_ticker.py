import yfinance
from yfin_downloader.utils import save_pickle, load_pickle


def download_stock_history(ticker, data_dir, period='1mo'):
    print('downloading %s' % ticker)
    stock = yfinance.Ticker(ticker)
    df = stock.history(period=period)
    if not df.empty:
        save_pickle(df, '%s/%s_prices.pkl' % (data_dir, ticker))
        return True
    return False


if __name__ == '__main__':
    ticker = 'TSNP'
    df = load_pickle('./%s_prices.pkl' % ticker)
    #download_stock_history('TSNP', '.', '6mo')
    print(df.head(20))
    df.to_csv('%s_prices.csv' % ticker, float_format="%.8f")
