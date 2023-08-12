from django.urls import path
from .views import ProductList, HealthTipList

urlpatterns = [
    path('products', ProductList.as_view()),
    path('healthtips', HealthTipList.as_view()),
    

]