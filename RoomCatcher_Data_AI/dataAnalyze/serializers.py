from rest_framework import serializers
from .models import Product, Tag, ProductTag, ProductKB

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        
class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = "__all__"
        
class ProductKBSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductKB
        fields = "__all__"