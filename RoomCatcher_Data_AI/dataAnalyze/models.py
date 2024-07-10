from django.db import models

# Create your models here.
class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    productName = models.CharField(max_length=30)
    productRoomType = models.CharField(max_length=30)
    productSellingType = models.CharField(max_length=30)
    productPrice = models.CharField(max_length=30)
    productAddr = models.CharField(max_length=50)
    productInfo = models.CharField(max_length=200)
    productImage = models.CharField(max_length=200)
    productIsContract = models.BooleanField()
    productIsQuick = models.BooleanField()
    
    class Meta:
        db_table = 'dataAnalyze_product'

class Tag(models.Model):
    id = models.IntegerField(primary_key=True)
    tagName = models.CharField(max_length=30)

class ProductTag(models.Model):
    id = models.IntegerField(primary_key=True)
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)
    tagId = models.ForeignKey(Tag, on_delete=models.CASCADE)