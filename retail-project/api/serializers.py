from products.models import Product, HealthTip, ProductCategory, HealthTipCategory
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


class ProductCategorySerializer(serializers.ModelSerializer):
     # create serializer class for ProductCategory model

    class Meta:
        model = ProductCategory
        fields = ('__all__')


class HealthTipCategorySerializer(serializers.ModelSerializer):
    # create serializer class for HealthTipCategory model

    class Meta:
        model = HealthTipCategory
        fields = ('__all__')


