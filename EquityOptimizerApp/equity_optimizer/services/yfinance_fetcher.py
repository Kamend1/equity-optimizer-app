import yfinance as yf
import pandas as pd
from requests.exceptions import HTTPError
from yfinance.exceptions import YFChartError
from .data_fetcher import DataFetcher


class YFinanceFetcher(DataFetcher):
    def fetch_stock_info(self, ticker: str) -> dict:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info:
                print(f"Warning: No data found for ticker '{ticker}'. It may be delisted or invalid.")
                return {}
            return info
        except YFChartError:
            print(f"Error: Ticker '{ticker}' may be delisted or invalid. Skipping.")
            return {}
        except HTTPError as http_err:
            print(f"HTTP Error: Failed to fetch info for ticker '{ticker}': {http_err}")
            return {}
        except Exception as e:
            print(f"Unexpected Error: Failed to fetch info for ticker '{ticker}': {e}")
            return {}

    def download_historical_data(self, ticker: str, start_date: str) -> pd.DataFrame:
        try:
            data = yf.download(ticker, start=start_date, interval='1d')
            if data.empty:
                print(f"Warning: No historical data found for ticker '{ticker}'. It may be delisted or invalid.")
                return pd.DataFrame()
            return data
        except YFChartError as e:
            print(f"YFChartError: Ticker '{ticker}' may be delisted or invalid. Error: {e}. Skipping.")
            return pd.DataFrame()
        except HTTPError as http_err:
            print(f"HTTP Error: Failed to download data for ticker '{ticker}': {http_err}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Unexpected Error: Failed to download data for ticker '{ticker}': {e}")
            return pd.DataFrame()
