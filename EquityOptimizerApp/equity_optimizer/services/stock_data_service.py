import pandas as pd
from django.db import transaction
from django.db.models import Count

from EquityOptimizerApp.currencies.models import ExchangeRate
from EquityOptimizerApp.equity_optimizer.models import StockData
from EquityOptimizerApp.equity_optimizer.services import DataFetcher, StockService
from EquityOptimizerApp.equity_optimizer.utils import percentage_return_classifier


class StockDataService:
    def __init__(self, fetcher: DataFetcher):
        self.fetcher = fetcher

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

            data['daily_return'] = data['Adj Close'].pct_change() * 100
            data['trend'] = data['daily_return'].apply(percentage_return_classifier)
            data.reset_index(inplace=True)

            for _, row in data.iterrows():
                date_value = pd.to_datetime(row['Date']).date()
                record_key = (stock.id, date_value)

                # Fetch the exchange rate if the currency is not USD
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
                        adj_close_to_usd = None  # Fallback if no exchange rate is found
                else:
                    adj_close_to_usd = row['Adj Close']

                record = StockData(
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

                if record_key in existing_records_set:
                    update_stock_data_objects.append(record)
                else:
                    stock_data_objects.append(record)

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
    def fetch_stock_data(stock_symbols, start_date='2010-01-01', end_date=None):
        """
        Fetch historical stock data for given stock symbols from the database and return as a DataFrame.
        """
        try:
            if not stock_symbols:
                raise ValueError("No stock symbols provided.")

            if start_date is None:
                start_date = '2010-01-01'

            if end_date is None:
                end_date = pd.Timestamp.now().strftime('%Y-%m-%d')

            stock_data = StockData.objects.filter(
                stock__ticker__in=stock_symbols,
                date__gte=start_date,
                date__lte=end_date
            ).select_related('stock')

            if not stock_data.exists():
                raise ValueError("No historical data found for the provided stock symbols and date range.")

            data_list = list(stock_data.values('stock__ticker', 'date', 'adj_close'))
            for data in data_list:
                data['adj_close'] = float(data['adj_close'])

            df = pd.DataFrame(data_list)

            if df.empty:
                raise ValueError("Converted DataFrame is empty.")

            close_price_df = df.pivot(index='date', columns='stock__ticker', values='adj_close')

            with pd.option_context('future.no_silent_downcasting', True):
                close_price_df.infer_objects(copy=False).fillna(0)

            close_price_df.reset_index(inplace=True)

            numeric_cols = close_price_df.columns.difference(['date'])
            close_price_df[numeric_cols] = close_price_df[numeric_cols].astype(float)

            return close_price_df

        except Exception as e:
            print(f"Error fetching stock data: {str(e)}")
            raise

    @staticmethod
    def get_stock_data_by_ticker(ticker, start_date, end_date):
        """Fetch stock data for a given ticker and date range."""
        stock_data = StockData.objects.filter(
            stock__ticker=ticker,
            date__range=[start_date, end_date]
        ).values('date', 'open', 'high', 'low', 'close', 'adj_close', 'volume', 'daily_return')

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
