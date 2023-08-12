from products.models import Product, HealthTip
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    # create serializer class for Product model

    class Meta:
        model = Product
        fields = ('__all__')


class HealthTipSerializer(serializers.ModelSerializer):
    # create serializer class for HealthTip model

    class Meta:
        model = HealthTip
        fields = ('__all__')

