from abc import ABC, abstractmethod


class DataFetcher(ABC):
    @abstractmethod
    def fetch_stock_info(self, ticker):
        pass

    @abstractmethod
    def download_historical_data(self, ticker, start_date):
        pass
