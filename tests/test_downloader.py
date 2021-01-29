import unittest
from unittest.mock import Mock
from unittest.mock import patch
from yfin_downloader.downloader import download_stock_history


class BasicTests(unittest.TestCase):

    @patch('yfin_downloader.downloader.yfinance.Ticker.history')
    def test_request_ticker_df_patch(self, mock_df):
        mock_df.return_value.ndim = 2
        df = download_stock_history("SPY")
        self.assertEqual(df.ndim, 2)

    def test_request_ticker_df_with(self):
        with patch('yfin_downloader.downloader.yfinance.Ticker.history') as mock_history:
            mock_history.return_value.ndim = 2
            df = download_stock_history("SPY")
            mock_history.assert_called_with(period='1mo')
            mock_history.assert_called_once()
            self.assertEqual(df.ndim, 2)

    def test_request_ticker_df(self):
        with patch('yfin_downloader.downloader.yfinance.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_ticker.return_value = mock_stock
            mock_stock.history.return_value.ndim = 2

            df = download_stock_history("SPY")

            mock_ticker.assert_called_with("SPY")
            mock_stock.history.assert_called_once()
            mock_stock.history.assert_called_with(period='1mo')
            self.assertEqual(df.ndim, 2)


if __name__ == "__main__":
    unittest.main()
