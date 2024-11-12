from django.db.models import Q
from .data_fetcher import DataFetcher
from ..models import Stock
from ..utils import parse_date


class StockService:
    def __init__(self, fetcher: DataFetcher):
        self.fetcher = fetcher

    @staticmethod
    def fetch_single_stock(ticker):
        return Stock.objects.filter(ticker=ticker).first()

    @staticmethod
    def get_all_stocks():
        return Stock.objects.all()

    @staticmethod
    def get_all_listed_stocks():
        return Stock.objects.filter(delisted=False)

    @staticmethod
    def get_filtered_stocks(query):
        return Stock.objects.filter(
            Q(ticker__icontains=query) |
            Q(name__icontains=query) |
            Q(sector__icontains=query)
        ).order_by('ticker')

    @staticmethod
    def check_stock_exists(ticker):
        """
        Checks if a stock with the given ticker already exists in the Stock model.
        """
        return Stock.objects.filter(ticker=ticker).exists()

    def add_stock_to_db(self, ticker):
        info = self.fetcher.fetch_stock_info(ticker)

        if not info:
            raise ValueError("No data returned from yfinance.")

        ex_dividend_date = parse_date(info.get('exDividendDate'))
        last_dividend_date = parse_date(info.get('lastDividendDate'))

        # Create or update the Stock instance
        stock = Stock.objects.create(
            ticker=ticker,
            name=info.get('shortName', ''),
            sector=info.get('sector', ''),
            industry=info.get('industry', ''),
            website=info.get('website', ''),
            logo_url=info.get('logo_url', ''),

            # Market Data
            market_cap=info.get('marketCap'),
            enterprise_value=info.get('enterpriseValue'),
            trailing_pe=info.get('trailingPE'),
            forward_pe=info.get('forwardPE'),
            peg_ratio=info.get('pegRatio'),
            price_to_book=info.get('priceToBook'),
            beta=info.get('beta'),

            # Valuation Metrics
            trailing_eps=info.get('trailingEps'),
            forward_eps=info.get('forwardEps'),
            book_value=info.get('bookValue'),
            fifty_two_week_high=info.get('fiftyTwoWeekHigh'),
            fifty_two_week_low=info.get('fiftyTwoWeekLow'),
            fifty_day_average=info.get('fiftyDayAverage'),

            # Financial Data
            revenue=info.get('totalRevenue'),
            gross_profit=info.get('grossProfits'),
            ebitda=info.get('ebitda'),
            net_income=info.get('netIncome'),
            diluted_eps=info.get('dilutedEPSTTM'),
            profit_margin=info.get('profitMargins'),
            operating_margin=info.get('operatingMargins'),

            # Balance Sheet Data
            total_cash=info.get('totalCash'),
            total_debt=info.get('totalDebt'),
            total_assets=info.get('totalAssets'),
            total_liabilities=info.get('totalLiab'),

            # Dividend Data
            dividend_yield=info.get('dividendYield'),
            dividend_rate=info.get('dividendRate'),
            payout_ratio=info.get('payoutRatio'),
            ex_dividend_date=ex_dividend_date,
            last_dividend_date=last_dividend_date,

            # Company Profile
            address1=info.get('address1', ''),
            city=info.get('city', ''),
            state=info.get('state', ''),
            country=info.get('country', ''),
            phone=info.get('phone', ''),
            full_time_employees=info.get('fullTimeEmployees'),

            # Company Summary
            long_business_summary=info.get('longBusinessSummary', ''),

            # ESG (Sustainability) Data
            esg_scores=info.get('esgScores'),

            # Analyst Recommendations
            recommendations=info.get('recommendationKey', {})
        )

        return stock
