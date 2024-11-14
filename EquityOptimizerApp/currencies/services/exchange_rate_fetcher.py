from abc import ABC, abstractmethod
import pandas as pd


class ExchangeRateFetcher(ABC):
    @abstractmethod
    def fetch_exchange_rate_data(self, base_currency: str, target_currency: str, start_date: str) -> pd.DataFrame:
        pass
