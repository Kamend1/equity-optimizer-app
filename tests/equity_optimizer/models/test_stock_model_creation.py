from django.test import TestCase
from EquityOptimizerApp.equity_optimizer.models import Stock


class StockModelTestCase(TestCase):
    def setUp(self):
        # Arrange: Create a stock instance
        self.stock = Stock.objects.create(ticker='AAPL', name='Apple Inc.')

    def test_stock_creation(self):
        self.assertEqual(self.stock.ticker, 'AAPL')
        self.assertEqual(self.stock.name, 'Apple Inc.')

    def test_stock_str_representation(self):
        self.assertEqual(str(self.stock), 'AAPL - Apple Inc.')
