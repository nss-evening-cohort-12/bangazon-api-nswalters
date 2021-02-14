from django.urls import path
from .views import list_expensive_products

urlpatterns = [
    path('reports/expensiveproducts', list_expensive_products),
]
