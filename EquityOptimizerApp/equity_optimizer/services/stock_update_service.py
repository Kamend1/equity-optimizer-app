from datetime import datetime

import pandas as pd
from django.db import transaction
from django.db.models import Max

from EquityOptimizerApp.equity_optimizer.models import Stock, StockData
from EquityOptimizerApp.equity_optimizer.services import StockDataService, DataFetcher, YFinanceFetcher, StockService
from EquityOptimizerApp.equity_optimizer.utils import parse_date

fetcher: DataFetcher = YFinanceFetcher()
stock_service = StockService(fetcher)
stock_data_service = StockDataService(fetcher)


class StockUpdateService:

    @staticmethod
    def update_stock_data_trend_daily_return(date):

        queryset = StockData.objects.filter(date__gt=date)
        stock_data_objects = []

        for stock_data in queryset:
            daily_return = StockData.objects.calculate_daily_return(
                stock=stock_data.stock,
                date=stock_data.date,
                adj_close=stock_data.adj_close,
            )

            stock_data.daily_return = daily_return
            stock_data.trend = StockData.objects.calculate_trend(daily_return)
            stock_data_objects.append(stock_data)
        StockData.objects.bulk_update(stock_data_objects, fields=['daily_return', 'trend'])
        return stock_data_objects

    @staticmethod
    def update_stock_data():
        stocks = stock_service.get_all_listed_stocks()
        stock_objects = []

        try:
            min_date = datetime(2100, 1, 1).date()
            for stock in stocks:

                try:
                    info = fetcher.fetch_stock_info(stock.ticker)
                    if not info:
                        print(f"No stock info available for {stock.ticker}. Skipping further processing.")
                        continue

                except Exception as e:
                    print(f"No stock info available for {stock.ticker}. Skipping further processing.")
                    continue

                ex_dividend_date = parse_date(info.get('exDividendDate'))
                last_dividend_date = parse_date(info.get('lastDividendDate'))

                stock_objects.append(
                    Stock(
                        id=stock.id,
                        name=info.get('shortName', stock.name),
                        sector=info.get('sector', stock.sector),
                        industry=info.get('industry', stock.industry),
                        website=info.get('website', stock.website),
                        logo_url=info.get('logo_url', stock.logo_url),

                        # Market Data
                        market_cap=info.get('marketCap', stock.market_cap),
                        enterprise_value=info.get('enterpriseValue', stock.enterprise_value),
                        trailing_pe=info.get('trailingPE', stock.trailing_pe),
                        forward_pe=info.get('forwardPE', stock.forward_pe),
                        peg_ratio=info.get('pegRatio', stock.peg_ratio),
                        price_to_book=info.get('priceToBook', stock.price_to_book),
                        beta=info.get('beta', stock.beta),

                        # Valuation Metrics
                        trailing_eps=info.get('trailingEps', stock.trailing_eps),
                        forward_eps=info.get('forwardEps', stock.forward_eps),
                        book_value=info.get('bookValue', stock.book_value),
                        fifty_two_week_high=info.get('fiftyTwoWeekHigh', stock.fifty_two_week_high),
                        fifty_two_week_low=info.get('fiftyTwoWeekLow', stock.fifty_two_week_low),
                        fifty_day_average=info.get('fiftyDayAverage', stock.fifty_day_average),

                        # Financial Data (Updated)
                        revenue=info.get('totalRevenue', stock.revenue),
                        gross_profit=info.get('grossMargins', 0) * info.get('totalRevenue', 0),
                        # Estimate using grossMargins
                        ebitda=info.get('ebitda', stock.ebitda),
                        net_income=info.get('netIncomeToCommon', stock.net_income),
                        diluted_eps=info.get('trailingEps', stock.diluted_eps),
                        profit_margin=info.get('profitMargins', stock.profit_margin),
                        operating_margin=info.get('operatingMargins', stock.operating_margin),

                        # Balance Sheet Data (Updated)
                        total_cash=info.get('totalCash', stock.total_cash),
                        total_debt=info.get('totalDebt', stock.total_debt),
                        total_assets=info.get('totalCash', 0) + info.get('totalDebt', 0),
                        # Estimate if totalAssets is missing
                        total_liabilities=info.get('totalDebt', stock.total_liabilities),

                        # Dividend Data
                        dividend_yield=info.get('dividendYield', stock.dividend_yield),
                        dividend_rate=info.get('dividendRate', stock.dividend_rate),
                        payout_ratio=info.get('payoutRatio', stock.payout_ratio),
                        ex_dividend_date=parse_date(info.get('exDividendDate')),
                        last_dividend_date=parse_date(info.get('lastDividendDate')),

                        # Company Profile
                        address1=info.get('address1', stock.address1),
                        city=info.get('city', stock.city),
                        state=info.get('state', stock.state),
                        country=info.get('country', stock.country),
                        phone=info.get('phone', stock.phone),
                        full_time_employees=info.get('fullTimeEmployees', stock.full_time_employees),
                        long_business_summary=info.get('longBusinessSummary', stock.long_business_summary),

                        # ESG (Sustainability) Data
                        esg_scores=info.get('esgScores', stock.esg_scores),

                        # Analyst Recommendations
                        recommendations=info.get('recommendationKey', stock.recommendations)
                    )
                )

                last_update = StockData.objects.filter(stock=stock).aggregate(
                    last_update=Max('updated_at')
                )['last_update']

                if not last_update:
                    start_date = '2010-01-01'
                else:
                    start_date = last_update.date()

                if start_date < min_date:
                    min_date = start_date

                previous_working_day = pd.to_datetime(min_date) - pd.tseries.offsets.BDay(2)
                formatted_date = previous_working_day.strftime('%Y-%m-%d')

                # start_date = '2024-11-08'
        except Exception as e:
            print(f"Failed to update stock data: {e}")

        print(start_date, min_date, formatted_date)
        stock_data_objects = stock_data_service.download_and_save_stock_data(stocks, formatted_date)
        StockUpdateService.update_stock_data_trend_daily_return(formatted_date)

        with transaction.atomic():
            Stock.objects.bulk_update(
                stock_objects,
                [
                    'name', 'sector', 'industry', 'website', 'logo_url',
                    'market_cap', 'enterprise_value', 'trailing_pe', 'forward_pe',
                    'peg_ratio', 'price_to_book', 'beta', 'trailing_eps', 'forward_eps',
                    'book_value', 'fifty_two_week_high', 'fifty_two_week_low', 'fifty_day_average',
                    'revenue', 'gross_profit', 'ebitda', 'net_income', 'diluted_eps',
                    'profit_margin', 'operating_margin', 'total_cash', 'total_debt',
                    'total_assets', 'total_liabilities', 'dividend_yield', 'dividend_rate',
                    'payout_ratio', 'ex_dividend_date', 'last_dividend_date',
                    'address1', 'city', 'state', 'country', 'phone',
                    'full_time_employees', 'long_business_summary', 'esg_scores', 'recommendations'
                ]
            )

            print("Stock data updated successfully.")
            return stock_data_objects
