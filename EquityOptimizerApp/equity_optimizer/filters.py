from django_filters import rest_framework as filters
from .models import StockData


class StockDataFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name="date", lookup_expr='gte')
    end_date = filters.DateFilter(field_name="date", lookup_expr='lte')
    ticker = filters.CharFilter(field_name="stock__ticker", lookup_expr="iexact")

    class Meta:
        model = StockData
        fields = ['ticker', 'start_date', 'end_date']
