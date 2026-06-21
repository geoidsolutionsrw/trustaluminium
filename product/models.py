from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from authentication.models import BaseModel
from django.db import models


class Product(BaseModel):
    productid = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    brand = models.CharField(max_length=200)
    price = models.FloatField()
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, null=True, on_delete=models.CASCADE)  

    # def __str__(self):
    #     return f"{self.product_name} - ${self.price} (Qty: {self.quantity})"
class Stock(BaseModel):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_quantity=models.IntegerField()
    instock_date=models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    
    
class Supplier(BaseModel):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=100)
    contact_person =models.CharField(max_length=100,null=True)
    phone_number = models.CharField(max_length=20)
    email_address = models.EmailField(max_length=50)
    country = models.CharField(max_length=50)
    address=models.CharField(max_length=200)
    creator=models.ForeignKey(User,null=True, on_delete=models.CASCADE )
    created_on=models.DateTimeField(auto_now=True)

class Customer(BaseModel):
    cust_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email_address = models.EmailField(max_length=50)
    address=models.CharField(max_length=200,null=True)
    tin=models.CharField(max_length=50,null=True)
    customer_type = models.CharField(max_length=50, null=True,choices=[
        ('Individual', 'Individual'),
        ('Company', 'Company')
    ])
    creator=models.ForeignKey(User,null=True, on_delete=models.CASCADE )
    created_on=models.DateTimeField(auto_now=True)
    



