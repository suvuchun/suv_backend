from rest_framework import serializers
from .models import User, Products, Orders, OrderItem, Category


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):


    items = OrderItemSerializer(many=True, read_only=True)
    products = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(), many=True, write_only=True
    )


    class Meta:
        model = Orders
        fields = [
            'user',
            'user_number',
            'products',
            'items',
            'address',

        ]
