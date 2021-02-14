from django.urls import path
from .views import list_expensive_products, list_inexpensive_products

urlpatterns = [
    path('reports/expensiveproducts', list_expensive_products),
    path('reports/inexpensiveproducts', list_inexpensive_products),
]
