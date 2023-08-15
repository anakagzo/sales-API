from django.urls import path
from .views import ProductList, HealthTipList, ProductCategoryList,\
      HealthTipCategoryList

urlpatterns = [
    path('products', ProductList.as_view()),
    path('healthtips', HealthTipList.as_view()),
    path('productCategory', ProductCategoryList.as_view()),
    path('healthtipCategory', HealthTipCategoryList.as_view()),  

]