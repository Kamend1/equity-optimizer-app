import math

from rest_framework import serializers
from .models import Stock


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