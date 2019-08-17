from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey

User = get_user_model()

def category_image_path(instance, filename):
    return "category/icons/{}/{}".format(instance.name, filename)

def product_image_path(instance, filename):
    return "product/images/{}/{}".format(instance.title, filename)


class Category(MPTTModel):
    name = models.CharField(max_length=200)
    icon = models.ImageField(upload_to=category_image_path, blank=True)
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    user = models.ForeignKey(User, related_name='user_product', on_delete=models.CASCADE)
    category = TreeForeignKey(Category, related_name='product_category', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    image = models.ImageField(upload_to=product_image_path, blank=True)
    description = models.TextField(null=True, blank=True)
    quantity = models.IntegerField(default=0)
    views = models.IntegerField(default=0)

class ProductViews(TimeStampedModel):
    ip = models.CharField(max_length=250)
    product = models.ForeignKey(Product, related_name='product_views', on_delete=models.CASCADE)