from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from .customer import Customer
from .product import Product
from .productcategory import ProductCategory
from .orderproduct import OrderProduct
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE


class LikeProduct(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING,)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING,)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'product'], name="unique product likes")
        ]
