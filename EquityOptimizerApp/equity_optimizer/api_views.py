from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .filters import StockDataFilter
from .services import stock_service, stock_data_service  # Assuming these are your service modules

from .models import Stock, StockData
from .serializers import StockSerializer, StockDataSerializer
from .services import StockDataService, StockService, DataFetcher, YFinanceFetcher

fetcher: DataFetcher = YFinanceFetcher()
stock_service = StockService(fetcher)
stock_data_service = StockDataService(fetcher)


class StockListAPIView(ListAPIView):
    queryset = Stock.objects.filter(delisted=False).order_by('ticker')
    queryset = Stock.objects.annotate_with_latest_adj_close(queryset)

    serializer_class = StockSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['ticker', 'name', 'sector']
    ordering_fields = ['market_cap', 'price_to_book', 'trailing_pe',
                       'forward_pe', 'dividend_yield', 'beta', 'latest_adj_close']
    ordering = ['ticker']


class StockDetailAPIView(RetrieveAPIView):
    queryset = Stock.objects.all()
    queryset = Stock.objects.annotate_with_latest_adj_close(queryset)
    serializer_class = StockSerializer
    lookup_field = 'ticker'
    lookup_url_kwarg = 'ticker'


@extend_schema(
    summary="Add a stock by ticker",
    description="Provide a stock ticker to add it to the database.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., AAPL, TSLA)"
                }
            },
            "example": {"ticker": "AAPL"}
        }
    },
    responses={
        201: {"description": "Stock added successfully."},
        400: {"description": "Invalid input or stock already exists."}
    }
)
class AddStockAPIView(CreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        ticker = request.data.get('ticker')

        if not ticker:
            return Response({'error': 'Ticker is required'}, status=status.HTTP_400_BAD_REQUEST)

        if stock_service.check_stock_exists(ticker):
            return Response({'error': 'Stock already exists'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            stock = stock_service.add_stock_to_db(ticker)
            stock_data_service.download_and_save_stock_data([stock])

            return Response({'message': f'Stock {ticker} added successfully!'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StockDataPagination(PageNumberPagination):
    page_size = 10


class StockDataListAPIView(ListAPIView):
    queryset = StockData.objects.all()
    serializer_class = StockDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StockDataFilter
    # pagination_class = StockDataPagination
