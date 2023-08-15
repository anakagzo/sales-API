from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import views, status
from rest_framework.response import Response
from products.models import Product, HealthTip, ProductCategory, HealthTipCategory
from .serializers import ProductSerializer, HealthTipSerializer, ProductCategorySerializer, HealthTipCategorySerializer
from random import randint
import retail.secret as secret


class ProductList(views.APIView):
    
    def get(self, request, format=None):
        # get the list of all products from the database
        # there are three query parameters that may be passed: name, brand, category
        token = secret.APIKEY

        if 'token' in request.GET and request.GET['token'] == token:
            # ensure the user has permission to access the database
            if 'cat' in request.GET:
                # check if category was passed
                category = request.GET['cat']
                if Product.objects.filter(category__iexact=category).exists():
                    products = Product.objects.filter(category__iexact=category)
                    if products.count() > 100:
                        # derive a mathematical function to select 100 products at random
                        # when the returned products are more than 100
                        limit = products.count() - 99
                        random_num = randint(0, limit)
                        random_products = products[random_num:random_num+100]
                        serializer = ProductSerializer(random_products, many=True)
                        return Response(serializer.data)
                    else:
                        serializer = ProductSerializer(products, many=True)
                        return Response(serializer.data)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            elif 'brand' in request.GET and 'name' in request.GET:
                # check if brand and name was passed
                brand = request.GET['brand']
                name = request.GET['name']
                if Product.objects.filter(name__iexact=name, brand__iexact=brand).exists():
                    product = Product.objects.filter(name__iexact=name, brand__iexact=brand)
                    serializer = ProductSerializer(product, many=True)
                    return Response(serializer.data) 
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            elif 'name' in request.GET:
                # if only one parameter was passed
                item = request.GET['name']
                if Product.objects.filter(name__iexact=item).exists():
                    # search the database with name keyword (look for exact match)
                    products = Product.objects.filter(name__iexact=item)
                    serializer = ProductSerializer(products, many=True)
                    return Response(serializer.data)
                elif Product.objects.filter(name__icontains=item).exists():
                    # search the database with name keyword (find the occurence in any name)
                    products = Product.objects.filter(name__icontains=item)
                    serializer = ProductSerializer(products, many=True)
                    return Response(serializer.data)
                elif Product.objects.filter(brand__iexact=item).exists():
                    # search the database with brand keyword
                    products = Product.objects.filter(brand__iexact=item)
                    serializer = ProductSerializer(products, many=True)
                    return Response(serializer.data)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                # if no query parameter was passed return all products 
                # (if total number of products is less than 16 products),
                #  else randomly select 16 products
                products = Product.objects.all()
                if products.count() > 16:  
                    limit = products.count() - 15
                    random_num = randint(0, limit)
                    random_products = products[limit: limit+16] 
                    serializer = ProductSerializer(random_products, many=True)
                    return Response(serializer.data)
                else:
                    serializer = ProductSerializer(products, many=True)
                    return Response(serializer.data)
        else:
            # the token means the user doesnt have permission to view the database
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class ProductCategoryList(views.APIView):
   
    def get(self, request, format=None):
        # get the list of all product categories from the database

        token = secret.APIKEY
        if 'token' in request.GET and request.GET['token'] == token:
            # ensure the user has permission to access the database
            categorylist = ProductCategory.objects.all()
            serializer = ProductCategorySerializer(categorylist, many=True)
            return Response(serializer.data)
        else:
           # the token means the user doesnt have permission to view the database
            return Response(status=status.HTTP_401_UNAUTHORIZED)     


class HealthTipList(views.APIView):

    def get(self, request, format=None):
        # get the list of all health tips from the database
        # there are two query parameters that may be passed: title, category
        token = secret.APIKEY

        if 'token' in request.GET and request.GET['token'] == token:
            # ensure the user has permission to access the database
            if 'cat' in request.GET:
                # check if category was passed
                category = request.GET['cat']
                if HealthTip.objects.filter(category__iexact=category).exists():
                    healthtips = HealthTip.objects.filter(category__iexact=category)
                    if healthtips.count() > 10:
                        # derive a mathematical function to select 10 healthtips at random
                        # when the returned healthtips are more than 10
                        limit = healthtips.count() - 9
                        random_num = randint(0, limit)
                        random_healthtips = healthtips[random_num:random_num+100]
                        serializer = HealthTipSerializer(random_healthtips, many=True)
                        return Response(serializer.data)
                    else:
                        serializer = HealthTipSerializer(healthtips, many=True)
                        return Response(serializer.data)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            elif 'title' in request.GET:
                # if title parameter was passed
                item = request.GET['title']
                if HealthTip.objects.filter(title__iexact=item).exists():
                    # search the database with title keyword (look for exact match)
                    healthtips = HealthTip.objects.filter(title__iexact=item)
                    serializer = HealthTipSerializer(healthtips, many=True)
                    return Response(serializer.data)
                elif HealthTip.objects.filter(title__icontains=item).exists():
                    # search the database with title keyword (find the occurence in any title)
                    healthtips = HealthTip.objects.filter(title__icontains=item)
                    serializer = HealthTipSerializer(healthtips, many=True)
                    return Response(serializer.data)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                # if no query parameter was passed return all healthtips 
                # (if total number of healthtips is less than 10),
                #  else randomly select 10 healthtips    
                healthtips = HealthTip.objects.all()
                if healthtips.count() > 10:  
                    limit = healthtips.count() - 9
                    random_num = randint(0, limit)
                    random_healthtips = healthtips[limit: limit+10] 
                    serializer = HealthTipSerializer(random_healthtips, many=True)
                    return Response(serializer.data)
                else:
                    serializer = HealthTipSerializer(healthtips, many=True)
                    return Response(serializer.data)
        else:
            # the token means the user doesnt have permission to view the database
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class HealthTipCategoryList(views.APIView):
   
    def get(self, request, format=None):
        # get the list of all health tip categories from the database

        token = secret.APIKEY
        if 'token' in request.GET and request.GET['token'] == token:
            # ensure the user has permission to access the database
            categorylist = HealthTipCategory.objects.all()
            serializer = HealthTipCategorySerializer(categorylist, many=True)
            return Response(serializer.data)
        else:
           # the token means the user doesnt have permission to view the database
            return Response(status=status.HTTP_401_UNAUTHORIZED)     


        
    
