import os
import django
from datetime import timedelta
from django.utils.timezone import now
import yfinance as yf
import csv


# Step 1: Set up Django settings environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EquityOptimizerApp.settings')  # Replace 'your_project' with your actual project name
django.setup()

from EquityOptimizerApp.equity_optimizer.models import Stock, StockData
# from EquityOptimizerApp.equity_optimizer.services import check_stock_exists, add_stock_to_db, download_and_save_stock_data


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


def add_stock(tickers):

    for ticker in tickers:
        if ticker:
            # Check if the stock already exists
            if check_stock_exists(ticker):
                print(f'Stock with ticker {ticker} already exists')
                continue
            else:
                try:
                    # Add the stock to the database
                    stock = add_stock_to_db(ticker)
                    # Download and save the historical stock data
                    download_and_save_stock_data(stock)
                except Exception as e:
                    # Handle the case where data retrieval fails
                    print(f'Failed to retrieve data for ticker {ticker}. Error: {str(e)}')

csv_file_path = "data/stock_data_2024_11_28.csv"

def upload_stock_data_from_csv(csv_file_path):
    """
    Reads a CSV file and uploads the data to the database.

    :param csv_file_path: Path to the CSV file.
    """
    try:
        # Open the CSV file
        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            # Iterate through each row in the CSV
            for row in reader:
                try:
                    # Fetch the related Stock object
                    stock = Stock.objects.get(id=row["stock_id"])

                    # Insert or update the StockData object
                    StockData.objects.update_or_create(
                        id=row["id"],  # Use the same ID for consistency
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
                    print(f"Stock with ID {row['stock_id']} does not exist. Skipping row.")
                except Exception as e:
                    print(f"Error processing row with ID {row['id']}: {e}")

        print("Data uploaded successfully.")

    except FileNotFoundError:
        print(f"File not found at location: {csv_file_path}")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")


upload_stock_data_from_csv(csv_file_path)