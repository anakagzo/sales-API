from django.db import models


# Create your models here.
class Product(models.Model):

    img = models.ImageField(upload_to='images/', default='images/IMG_1828_2.jpeg')
    name = models.CharField(max_length=40)
    brand = models.CharField(max_length=20)
    price = models.IntegerField()
    category = models.CharField(max_length=40)
    unit_code = models.CharField(max_length=10)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class ProductCategory(models.Model):

    name = models.CharField(max_length=40, unique=True, default='general')

    def __str__(self):
        return self.name
    

class HealthTip(models.Model):

    img = models.ImageField(upload_to='images/', default='images/IMG_1828_2.jpeg')
    title = models.CharField(max_length=40)
    category = models.CharField(max_length=40)
    content = models.TextField()

    def __str__(self):
        return self.title
    

class HealthTipCategory(models.Model):

    name = models.CharField(max_length=40, unique=True, default='general')

    def __str__(self):
        return self.name   

    