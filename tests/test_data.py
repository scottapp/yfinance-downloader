import unittest
from unittest.mock import patch
from yfin_downloader.downloader import download_stock_history


class BasicTests(unittest.TestCase):
    @patch('yahoofinance.downloader.yfinance.Ticker.history')
    def test_request_response_with_decorator(self, mock_df):
        """Mocking using a decorator"""
        mock_df.return_value.ndim = 2
        df = download_stock_history("SPY")

        # Assert that the request-response cycle completed successfully.
        self.assertEqual(df.ndim, 2)


if __name__ == "__main__":
    unittest.main()
