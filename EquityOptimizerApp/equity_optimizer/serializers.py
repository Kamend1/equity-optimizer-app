import math

from rest_framework import serializers
from .models import Stock, StockData


class StockSerializer(serializers.ModelSerializer):
    latest_adj_close = serializers.FloatField()

    class Meta:
        model = Stock
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        for key, value in data.items():
            if isinstance(value, float) and (math.isinf(value) or math.isnan(value)):
                data[key] = None

        return data


class StockDataSerializer(serializers.ModelSerializer):
    stock_name = serializers.SerializerMethodField()

    class Meta:
        model = StockData
        fields = [
            'id', 'stock', 'stock_name', 'date', 'open', 'high', 'low', 'close',
            'adj_close', 'volume', 'daily_return', 'trend', 'adj_close_to_usd'
        ]

    def get_stock_name(self, obj):
        return obj.stock.name

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for key, value in data.items():
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                data[key] = None
        return data