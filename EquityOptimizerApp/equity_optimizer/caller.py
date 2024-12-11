import os
import shutil
import django
from datetime import timedelta, datetime

import pandas as pd
from django.utils.timezone import now
import yfinance as yf
import csv

from EquityOptimizerApp import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EquityOptimizerApp.settings')
django.setup()
from EquityOptimizerApp.equity_optimizer.models import Stock, StockData
from EquityOptimizerApp.equity_optimizer.services import StockService, YFinanceFetcher

def manually_update_stock_data(date):

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


def get_manually_stock_data(ticker, start_date):
    stock = Stock.objects.filter(ticker=ticker).first()

    data = StockData.objects.filter(stock=stock, date__gt=start_date).order_by('date')

    return data


def save_stock_data_to_csv(date):
    try:
        target_date = datetime.strptime(date, '%Y-%m-%d').date()

        stock_data_queryset = StockData.objects.filter(date__gte=target_date).select_related('stock')

        if not stock_data_queryset.exists():
            print(f"No records found for date >= {target_date}.")
            return None

        stock_data = stock_data_queryset.values(
            'id', 'stock__ticker', 'date', 'open', 'high', 'low', 'close',
            'adj_close', 'volume', 'daily_return', 'trend', 'adj_close_to_usd'
        )
        df = pd.DataFrame(stock_data)

        data_dir = os.path.join(settings.BASE_DIR, 'data')
        os.makedirs(data_dir, exist_ok=True)

        file_name = f"stock_data_{date}.csv"
        file_path = os.path.join(data_dir, file_name)

        df.to_csv(file_path, index=False)

        print(f"Stock data saved to {file_path}")
        return file_path

    except ValueError as e:
        print(f"Invalid date format: {e}. Please use 'YYYY-MM-DD'.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def upload_stock_data_from_csv(date):
    data_dir = os.path.join(settings.BASE_DIR, 'data')
    csv_file_path = os.path.join(data_dir, f"stock_data_{date}.csv")

    try:
        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    # Fetch the stock using the ticker from the CSV
                    stock = Stock.objects.get(ticker=row["stock__ticker"])

                    StockData.objects.update_or_create(
                        id=row["id"],
                        defaults={
                            "stock": stock,
                            "date": row["date"],
                            "open": float(row["open"]),
                            "high": float(row["high"]),
                            "low": float(row["low"]),
                            "close": float(row["close"]),
                            "adj_close": float(row["adj_close"]),
                            "volume": int(row["volume"]),
                            "daily_return": float(row["daily_return"]) if row["daily_return"] else None,
                            "trend": row["trend"] if row["trend"] else None,
                            "adj_close_to_usd": float(row["adj_close_to_usd"]) if row["adj_close_to_usd"] else None,
                        },
                    )
                except Stock.DoesNotExist:
                    print(f"Stock with ticker {row['stock__ticker']} does not exist. Skipping row.")
                except Exception as e:
                    print(f"Error processing row with ID {row['id']}: {e}")

        print("Data uploaded successfully.")

        try:
            shutil.rmtree(data_dir)
            print(f"Data directory {data_dir} deleted successfully.")
        except Exception as e:
            print(f"Error deleting data directory {data_dir}: {e}")

    except FileNotFoundError:
        print(f"File not found at location: {csv_file_path}")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")


# def export_tickers_to_csv():
#
#     try:
#
#         data_dir = os.path.join(settings.BASE_DIR, 'data')
#         os.makedirs(data_dir, exist_ok=True)
#
#         file_path = os.path.join(data_dir, 'tickers.csv')
#
#         tickers = Stock.objects.values_list('ticker', flat=True)
#
#         with open(file_path, mode='w', newline='', encoding='utf-8') as file:
#             writer = csv.writer(file)
#             writer.writerow(['ticker'])  # Write header
#             for ticker in tickers:
#                 writer.writerow([ticker])  # Write each ticker
#
#         print(f"Tickers successfully exported to {file_path}")
#         return file_path
#
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None

def process_tickers_from_csv():

    fetcher = YFinanceFetcher()
    stock_service = StockService(fetcher)

    data_dir = os.path.join(settings.BASE_DIR, 'data')
    csv_file_path = os.path.join(data_dir, 'tickers.csv')


    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip the header row

            if 'ticker' not in header:
                raise ValueError("CSV file must contain a 'ticker' column.")

            for row in reader:
                try:
                    ticker = row[header.index('ticker')].strip()
                    if not ticker:
                        print("Skipping empty ticker.")
                        continue

                    if stock_service.check_stock_exists(ticker):
                        print(f"Stock with ticker '{ticker}' already exists. Skipping.")
                        continue

                    stock = stock_service.add_stock_to_db(ticker)
                    print(f"Successfully added stock: {stock.ticker}")

                except Exception as e:
                    print(f"Error processing ticker '{ticker}': {e}")

    except FileNotFoundError:
        print(f"File not found at location: {csv_file_path}")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")


def find_missing_tickers_in_csv():

    data_dir = os.path.join(settings.BASE_DIR, 'data')
    csv_file_path = os.path.join(data_dir, 'tickers.csv')

    try:

        heroku_tickers = set(Stock.objects.values_list('ticker', flat=True))


        csv_tickers = set()
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)

            if 'ticker' not in header:
                raise ValueError("CSV file must contain a 'ticker' column.")

            for row in reader:
                ticker = row[header.index('ticker')].strip()
                if ticker:
                    csv_tickers.add(ticker)

        missing_tickers = list(heroku_tickers - csv_tickers)

        return missing_tickers

    except FileNotFoundError:
        print(f"CSV file not found at location: {csv_file_path}")
        return []
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
        return []


# upload_stock_data_from_csv('2024-12-06')
# save_stock_data_to_csv('2024-12-06')
# process_tickers_from_csv()
# find_missing_tickers_in_csv()