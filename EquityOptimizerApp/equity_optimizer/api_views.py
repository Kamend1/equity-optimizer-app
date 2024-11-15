from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Stock, StockData
from .serializers import StockSerializer


class StockListAPIView(ListAPIView):
    queryset = Stock.objects.filter(delisted=False).order_by('ticker')
    queryset = Stock.objects.annotate_with_latest_adj_close(queryset)

    serializer_class = StockSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['ticker', 'name', 'sector']
    ordering_fields = ['market_cap', 'price_to_book', 'trailing_pe',
                       'forward_pe', 'dividend_yield', 'beta', 'latest_adj_close']
    ordering = ['ticker']
