from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from bot.models import Products,User
from bot.serizalizers import ProductSerializer, OrderSerializer


# Create your views here.
class CategoryAPIView(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Products.objects.all()

class ProductsAPIView(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Products.objects.all()

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        if category_id:
            return Products.objects.filter(category_id=category_id)
        return Products.objects.all()

class OrderAPIView(APIView):
    def post(self, request, *args, **kwargs):
        tg_id = request.data.get('user')
        try:
            user = User.objects.get(tg_id=tg_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        data = request.data.copy()
        data['user'] = user.id

        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

