from django.urls import path
from .views import list_expensive_products, list_inexpensive_products, list_completed_orders, list_incomplete_orders


urlpatterns = [
    path('reports/expensiveproducts', list_expensive_products),
    path('reports/inexpensiveproducts', list_inexpensive_products),
    path('reports/completedorders', list_completed_orders),
    path('reports/incompleteorders', list_incomplete_orders)
]
