import os
import django
from datetime import timedelta
from django.utils.timezone import now
import yfinance as yf


# Step 1: Set up Django settings environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EquityOptimizerApp.settings')  # Replace 'your_project' with your actual project name
django.setup()

from EquityOptimizerApp.equity_optimizer.models import Stock, StockData
from EquityOptimizerApp.equity_optimizer.services import check_stock_exists, add_stock_to_db, download_and_save_stock_data


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

manually_update_stock_data()