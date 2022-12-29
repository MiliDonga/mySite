from datetime import *

import PIL.Image
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=250)
    warehouse = models.CharField(max_length=250, default='None')

    def __str__(self):
        return self.name + ", " + self.warehouse


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=100, validators=[MaxValueValidator(1000), MinValueValidator(0)])
    available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    interested = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def refill(self):
        self.stock = self.stock + 100
        self.save()
        return self.stock


class Client(User):
    PROVINCE_CHOICES = [('AB', 'Alberta'), ('MB', 'Manitoba'), ('ON', 'Ontario'), ('QC', 'Quebec'), ]
    company = models.CharField(max_length=100, blank=True)
    shipping_address = models.CharField(max_length=350, null=True, blank=True)
    city = models.CharField(max_length=50, default='Windsor')
    province = models.CharField(max_length=2, choices=PROVINCE_CHOICES, default='ON')
    interested_in = models.ManyToManyField(Category)
    profile_photo = models.ImageField(upload_to='profile_photo/', blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.profile_photo:
            im = PIL.Image.open(self.profile_photo)
            width, height = im.size
            ratio = width / height

            N_height = 200
            N_width = int(N_height * ratio)
            im = im.resize((N_width, N_height))

            new_width = 200
            new_height = 200
            left = (N_width - new_width) / 2
            top = (N_height - new_height) / 2
            right = (N_width + new_width) / 2
            bottom = (N_height + new_height) / 2

            im = im.crop((left, top, right, bottom))
            im.save(self.profile_photo.path)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    num_units = models.PositiveIntegerField(default=0)
    order_status = [(0, 'Order Cancelled'), (1, 'Order Placed'), (2, 'OrderShipped'), (3, 'Order Delivered'), ]
    status_date = models.DateField(default=datetime.now)

    def total_cost(self):
        return self.num_units * self.product.price

    def __str__(self):
        return "Ordered " + str(self.id) + ", productName: " + str(self.product.name) + ", ClientID: " + str(
            self.client)
