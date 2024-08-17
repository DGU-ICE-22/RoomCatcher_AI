from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Product, ProductKB
from .serializers import ProductSerializer, ProductTagSerializer, TagSerializer, ProductKBSerializer
from .ver1.product_crawling import product_crawling
from .ver1.transpose_location_to_address_dabang import transpose_location_to_address
from django.db.models import Q

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self):
        products = Product.objects.all()
        serializer = serializer.ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 
           
    def create(self, request, *args, **kwargs):
        transpose_location_to_address()
        return Response(status=status.HTTP_201_CREATED)
    
class ProductFilterView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        address = self.request.query_params.get('address', None)
        tags = self.request.query_params.getlist('tag', None)

        if address:
            queryset = queryset.filter(address__icontains=address)

        if tags:
            query = Q()
            for tag in tags:
                query &= Q(tag__icontains=tag)
            queryset = queryset.filter(query)

        return queryset