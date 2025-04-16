import pandas as pd
from django.db import transaction
from django.db.models import Count
from pandas._libs.tslibs.offsets import BDay

from EquityOptimizerApp.currencies.models import ExchangeRate
from EquityOptimizerApp.currencies.services.exchange_rate_service import ExchangeRateService
from EquityOptimizerApp.equity_optimizer.models import StockData
from EquityOptimizerApp.equity_optimizer.services import DataFetcher, StockService
from EquityOptimizerApp.equity_optimizer.utils import percentage_return_classifier


class StockDataService:
    def __init__(self, fetcher: DataFetcher):
        self.fetcher = fetcher

    @staticmethod
    def create_new_record(stock, row, date_value, adj_close_to_usd):
        return StockData(
            stock=stock,
            date=date_value,
            open=row['Open'],
            high=row['High'],
            low=row['Low'],
            close=row['Close'],
            adj_close=row['Adj Close'],
            volume=row['Volume'],
            daily_return=row['daily_return'],
            trend=row['trend'],
            adj_close_to_usd=adj_close_to_usd,
        )

    @staticmethod
    def update_existing_record(record, row, adj_close_to_usd):
        record.open = row['Open']
        record.high = row['High']
        record.low = row['Low']
        record.close = row['Close']
        record.adj_close = row['Adj Close']
        record.volume = row['Volume']
        record.daily_return = row['daily_return']
        record.trend = row['trend']
        record.adj_close_to_usd = adj_close_to_usd
        return record

    @staticmethod
    def fetch_existing_records(stock_list):
        existing_records_set = set()
        for stock in stock_list:
            existing_dates = StockData.objects.filter(stock=stock).values_list('stock_id', 'date')
            existing_records_set.update(existing_dates)

        print(f"Debug: Found {len(existing_records_set)} existing records in the database.")

        return existing_records_set

    def download_historical_data(self, stock, start_date):
        try:
            data = self.fetcher.download_historical_data(stock.ticker, start_date)
            if data.empty:
                print(f"Warning: No data returned for {stock.ticker}. Skipping.")
                return None
            return data
        except Exception as e:
            print(f"Error: Ticker '{stock.ticker}' may be delisted or invalid. Skipping.")
            return None

    def process_stock_data(self, data, stock, existing_records_set):
        stock_data_objects = []
        update_stock_data_objects = []

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]

        data['daily_return'] = data['Adj Close'].pct_change() * 100
        data['trend'] = data['daily_return'].apply(percentage_return_classifier)
        data.reset_index(inplace=True)

        for _, row in data.iterrows():
            date_value = pd.to_datetime(row['Date']).date()
            record_key = (stock.id, date_value)

            adj_close_to_usd = (
                row['Adj Close'] / ExchangeRateService.get_exchange_rate(stock.currency_code, date_value)
                if stock.currency_code != 'USD'
                else row['Adj Close']
            )

            if record_key in existing_records_set:
                existing_record = StockData.objects.get(stock=stock, date=date_value)
                update_stock_data_objects.append(self.update_existing_record(existing_record, row, adj_close_to_usd))
            else:
                stock_data_objects.append(self.create_new_record(stock, row, date_value, adj_close_to_usd))

        return stock_data_objects, update_stock_data_objects

    @staticmethod
    def save_stock_data(stock_data_objects, update_stock_data_objects):
        with transaction.atomic():
            if update_stock_data_objects:
                fields_to_update = [
                    'date', 'open', 'high', 'low', 'close', 'adj_close',
                    'volume', 'daily_return', 'trend', 'adj_close_to_usd'
                ]
                StockData.objects.bulk_update(update_stock_data_objects, fields=fields_to_update, batch_size=1000)
                print(f"Updated {len(update_stock_data_objects)} records.")

            if stock_data_objects:
                StockData.objects.bulk_create(stock_data_objects, batch_size=1000)
                print(f"Created {len(stock_data_objects)} records.")

    # def download_and_save_stock_data(self, stock_list, start_date='2010-01-01'):
    #     stock_data_objects = []
    #     update_stock_data_objects = []
    #     existing_records_set = self.fetch_existing_records(stock_list)
    #
    #     for stock in stock_list:
    #         data = self.download_historical_data(stock, start_date)
    #         if data is None:
    #             continue
    #
    #         stock_data_objects, update_stock_data_objects = self.process_stock_data(data, stock, existing_records_set)
    #
    #     self.save_stock_data(stock_data_objects, update_stock_data_objects)
    #     return stock_data_objects, update_stock_data_objects

    def download_and_save_stock_data(self, stock_list, start_date='2010-01-01', interval='1d'):
        stock_data_objects = []
        update_stock_data_objects = []
        existing_records_set = set()

        for stock in stock_list:
            existing_dates = StockData.objects.filter(stock=stock).values_list('stock_id', 'date')
            existing_records_set.update(existing_dates)

        print(f"Debug: Found {len(existing_records_set)} existing records in the database.")

        for stock in stock_list:
            try:
                data = self.fetcher.download_historical_data(stock.ticker, start_date)
            except Exception as e:
                print(f"Error: Ticker '{stock.ticker}' may be delisted or invalid. Skipping.")
                continue

            if data.empty:
                print(f"Warning: No data returned for {stock.ticker}. Skipping.")
                continue

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0] for col in data.columns]

            data['daily_return'] = data['Adj Close'].pct_change() * 100
            data['trend'] = data['daily_return'].apply(percentage_return_classifier)
            data.reset_index(inplace=True)

            for _, row in data.iterrows():
                date_value = pd.to_datetime(row['Date']).date()
                record_key = (stock.id, date_value)

                if stock.currency_code != 'USD':
                    exchange_rate = (
                        ExchangeRate.objects.filter(
                            base_currency__code='USD',
                            target_currency__code=stock.currency_code,
                            date=date_value,
                        ).first()
                    )
                    if exchange_rate:
                        adj_close_to_usd = row['Adj Close'] / exchange_rate.rate
                    else:
                        adj_close_to_usd = None
                else:
                    adj_close_to_usd = row['Adj Close']

                if record_key in existing_records_set:
                    existing_record = StockData.objects.get(stock=stock, date=date_value)
                    existing_record.open = row['Open']
                    existing_record.high = row['High']
                    existing_record.low = row['Low']
                    existing_record.close = row['Close']
                    existing_record.adj_close = row['Adj Close']
                    existing_record.volume = row['Volume']
                    existing_record.daily_return = row['daily_return']
                    existing_record.trend = row['trend']
                    existing_record.adj_close_to_usd = adj_close_to_usd
                    update_stock_data_objects.append(existing_record)
                else:
                    # Create a new record
                    new_record = StockData(
                        stock=stock,
                        date=date_value,
                        open=row['Open'],
                        high=row['High'],
                        low=row['Low'],
                        close=row['Close'],
                        adj_close=row['Adj Close'],
                        volume=row['Volume'],
                        daily_return=row['daily_return'],
                        trend=row['trend'],
                        adj_close_to_usd=adj_close_to_usd,
                    )
                    stock_data_objects.append(new_record)

        print(f"Debug: Preparing to bulk update {len(update_stock_data_objects)} records.")
        print(f"Debug: Preparing to bulk create {len(stock_data_objects)} records.")

        with transaction.atomic():
            if update_stock_data_objects:
                fields_to_update = ['date', 'open', 'high', 'low', 'close', 'adj_close', 'volume', 'daily_return',
                                    'trend', 'adj_close_to_usd']
                try:
                    StockData.objects.bulk_update(update_stock_data_objects, fields=fields_to_update, batch_size=1000)
                    print(f"Debug: Successfully updated {len(update_stock_data_objects)} records.")
                except Exception as e:
                    print(f"Error during bulk_update: {e}")

            if stock_data_objects:
                try:
                    StockData.objects.bulk_create(stock_data_objects, batch_size=1000)
                    print(f"Debug: Successfully created {len(stock_data_objects)} records.")
                except Exception as e:
                    print(f"Error during bulk_create: {e}")

        return stock_data_objects + update_stock_data_objects

    @staticmethod
    def fetch_data_from_db(stock_symbols, start_date, end_date):
        return StockData.objects.filter(
            stock__ticker__in=stock_symbols,
            date__gte=start_date,
            date__lte=end_date
        ).select_related('stock')

    @staticmethod
    def convert_to_dataframe(stock_data):
        data_list = list(stock_data.values('stock__ticker', 'date', 'adj_close_to_usd'))
        df = pd.DataFrame(data_list)

        if df.empty:
            raise ValueError("Converted DataFrame is empty.")

        close_price_df = df.pivot(index='date', columns='stock__ticker', values='adj_close_to_usd')
        close_price_df.index = pd.to_datetime(close_price_df.index)
        return close_price_df

    @staticmethod
    def validate_common_dates(close_price_df, stock_symbols, start_date, end_date):
        results = []
        first_valid_index = pd.to_datetime(close_price_df.apply(lambda col: col.first_valid_index()).min())
        last_valid_index = pd.to_datetime(close_price_df.apply(lambda col: col.last_valid_index()).max())

        common_start_date = max(start_date, first_valid_index) if first_valid_index else start_date
        common_end_date = min(end_date, last_valid_index) if last_valid_index else end_date

        for ticker in stock_symbols:
            first_date = close_price_df[ticker].first_valid_index()
            last_date = close_price_df[ticker].last_valid_index()

            if first_date and first_date > common_start_date:
                results.append(
                    f"Stock {ticker} is missing data at the common start date ({common_start_date}). "
                    f"First available date: {first_date}."
                )

            if last_date and last_date < common_end_date:
                results.append(
                    f"Stock {ticker} is missing data at the common end date ({common_end_date}). "
                    f"Last available date: {last_date}."
                )

        if results:
            raise ValueError(f"Please check out the following stocks: {'\n'.join(results)}")

    @staticmethod
    def clean_and_align_data(close_price_df, start_date, end_date):
        all_dates = pd.date_range(start=start_date, end=end_date, freq='B')
        close_price_df = close_price_df.reindex(all_dates)
        close_price_df.fillna(method='bfill', inplace=True)
        close_price_df.fillna(method='ffill', inplace=True)
        close_price_df.fillna(0.00, inplace=True)
        close_price_df.reset_index(inplace=True)
        close_price_df.rename(columns={'index': 'date'}, inplace=True)
        return close_price_df

    @staticmethod
    def fetch_stock_data(stock_symbols, start_date='2010-01-01', end_date=None):

        start_date = pd.to_datetime(start_date) + BDay(0)
        end_date = pd.to_datetime(end_date) if end_date else pd.Timestamp.now()

        try:
            if not stock_symbols:
                raise ValueError("No stock symbols provided.")

            # Step 1: Fetch data from the database
            try:
                print("Fetching stock data from the database...")
                stock_data = StockDataService.fetch_data_from_db(stock_symbols, start_date, end_date)
                print(f"Step 1 - Stock data fetched: {len(stock_data)} records")
            except Exception as e:
                print(f"Error in Step 1 - Fetching stock data: {str(e)}")
                raise ValueError(f"Failed to fetch stock data from the database: {str(e)}")

            # Step 2: Convert the data to a DataFrame
            try:
                print("Converting stock data to DataFrame...")
                close_price_df = StockDataService.convert_to_dataframe(stock_data)
                print(f"Step 2 - DataFrame created with shape: {close_price_df.shape}")
                print(close_price_df)
            except Exception as e:
                print(f"Error in Step 2 - Converting to DataFrame: {str(e)}")
                raise ValueError(f"Failed to convert stock data to DataFrame: {str(e)}")

            # Step 3: Validate common start and end dates
            try:
                print("Validating common start and end dates across stocks...")
                StockDataService.validate_common_dates(close_price_df, stock_symbols, start_date, end_date)
                print(close_price_df)
                print("Step 3 - Date validation completed successfully")
            except Exception as e:
                print(f"Error in Step 3 - Validating dates: {str(e)}")
                raise ValueError(f"Date validation failed: {str(e)}")

            # Step 4: Clean and align data
            try:
                print("Cleaning and aligning stock data...")
                close_price_df = StockDataService.clean_and_align_data(close_price_df, start_date, end_date)
                print(close_price_df)
                print(f"Step 4 - Data cleaned and aligned. Final DataFrame shape: {close_price_df.shape}")
            except Exception as e:
                print(f"Error in Step 4 - Cleaning and aligning data: {str(e)}")
                raise ValueError(f"Failed to clean and align data: {str(e)}")

            return close_price_df

        except Exception as e:
            print(f"Error fetching stock data: {str(e)}")
            raise ValueError(f"Error fetching stock data: {str(e)}")

    @staticmethod
    def get_stock_data_by_ticker(ticker, start_date, end_date):
        """Fetch stock data for a given ticker and date range."""
        stock_data = StockData.objects.filter(
            stock__ticker=ticker,
            date__range=[start_date, end_date]
        ).values('date', 'open', 'high', 'low', 'close', 'adj_close', 'volume', 'daily_return', 'adj_close_to_usd',)

        df = pd.DataFrame(list(stock_data))
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        return df

    @staticmethod
    def get_trend_summary(ticker, start_date, end_date):
        """
        Get a summary of trends for a given stock within a specified date range.

        Args:
            ticker (str): The stock ticker symbol.
            start_date (str): The start date in 'YYYY-MM-DD' format.
            end_date (str): The end date in 'YYYY-MM-DD' format.

        Returns:
            pd.DataFrame: A DataFrame summarizing the trend counts.
        """
        stock = StockService.fetch_single_stock(ticker)

        trend_summary = StockData.objects.filter(
            stock=stock,
            date__range=[start_date, end_date]
        ).values('trend').annotate(count=Count('trend'))

        trend_summary_df = pd.DataFrame(list(trend_summary))

        return trend_summary_df

    @staticmethod
    def update_stock_data_trend_daily_return(date):

        queryset = StockData.objects.filter(date__gt=date)

        stock_data_objects = []

        for stock_data in queryset:
            # current_stock = Stock.objects.filter(pk=stock_data.stock).first()

            daily_return = StockData.objects.calculate_daily_return(
                stock=stock_data.stock,
                date=stock_data.date,
                adj_close=stock_data.adj_close,
            )

            stock_data.daily_return = daily_return
            stock_data.trend = StockData.objects.calculate_trend(daily_return)
            stock_data_objects.append(stock_data)
        StockData.objects.bulk_update(stock_data_objects, fields=['daily_return', 'trend'])
