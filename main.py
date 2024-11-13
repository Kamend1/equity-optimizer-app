import yfinance as yf
import pandas as pd
#
# # Set the ticker symbol for testing
# ticker_symbol = "AAPL"  # Change this to test different tickers
#
# # Create the Ticker object
# ticker = yf.Ticker(ticker_symbol)
#
# # Fetch stock information
# try:
#     stock_info = ticker.info
#     print(stock_info.keys())
#     print(f"Stock Information for {ticker_symbol}:")
#     print(stock_info)
#     print("\nSelected Fields:")
#     print(f"Gross Profit: {stock_info.get('grossProfits')}")
#     print(f"Net Income: {stock_info.get('netIncome')}")
#     print(f"Total Assets: {stock_info.get('totalAssets')}")
#     print(f"Total Liabilities: {stock_info.get('totalLiab')}")
# except Exception as e:
#     print(f"Failed to fetch stock info for {ticker_symbol}: {e}")
#
# # Fetch historical data
# try:
#     start_date = "2022-01-01"
#     data = ticker.history(start=start_date)
#     print(f"\nHistorical Data for {ticker_symbol} from {start_date}:")
#     print(data.head())
# except Exception as e:
#     print(f"Failed to fetch historical data for {ticker_symbol}: {e}")
#

# import os
# import django
#
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EquityOptimizerApp.settings')
#
# # Initialize Django
# django.setup()
#
# from EquityOptimizerApp.equity_optimizer.services import StockUpdateService
#
# StockUpdateService.update_stock_data_trend_daily_return('2024-11-08')

# ticker = 'SU.PA'
# stock_data = yf.Ticker(ticker)
# info = stock_data.info
#
# print(info['currency'])


