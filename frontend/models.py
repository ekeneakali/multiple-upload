
from django.db import models

from django.contrib.auth.models import User


# Create your models here.

class MultipleImage(models.Model):
    name = models.CharField(max_length=150)
    upload = models.FileField(upload_to='upload')
    price = models.IntegerField(default=0)
    product = models.CharField(max_length=50)



    def __str__(self):
        return self.name

    class Meta():
        verbose_name_plural = 'MultipleImage'

class Product(models.Model):
    name = models.CharField(max_length=50)
    image = models.FileField(upload_to="document")
    price = models.IntegerField()
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    favourite = models.ManyToManyField(User, related_name='favourite', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    
    def total_likes(self):
        return self.likes.count()

    class Meta():
        verbose_name_plural = 'Product'

# class Cart(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     product_qty = models.IntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


#     def __str__(self):
#         return self.product.name

#     class Meta():
#         verbose_name_plural = 'Cart'


class File(models.Model):
    title = models.CharField(max_length=50)
    files = models.FileField(upload_to="document")
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    
    class Meta():
        verbose_name_plural = 'File'


class NewsLetter(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta():
        verbose_name_plural = 'NewsLetter'



class Songs(models.Model):
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return self.song_title