import yfinance as yf
import pandas as pd
from .exchange_rate_fetcher import ExchangeRateFetcher


class YFinanceExchangeRateFetcher(ExchangeRateFetcher):
    def fetch_exchange_rate_data(self, base_currency: str, target_currency: str, start_date: str) -> pd.DataFrame:
        if base_currency == target_currency:
            return pd.DataFrame()

        ticker = f"{base_currency}{target_currency}=X"
        try:
            data = yf.Ticker(ticker).history(start=start_date)
            if data.empty:
                print(f"Warning: No data found for ticker '{ticker}'.")
                return pd.DataFrame()
            return data
        except Exception as e:
            print(f"Error: Failed to fetch exchange rate data for '{ticker}'. Error: {e}")
            return pd.DataFrame()
