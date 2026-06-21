from django.db import models
from django.db import models
from django.contrib.auth.models import User

from product.models import Customer  # Import from customer app
from product.models import Product   # Import from product app
from authentication.models import BaseModel


class Quotation(BaseModel):
    QUOTATION_STATUS = (
        ('ACCEPTED', 'ACCEPTED'),
        ('MODIFICATION REQUESTED', 'MODIFICATION REQUESTED'),
        ('PENDING', 'PENDING'),
    )
    
    quo_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quotation_status = models.CharField(max_length=40, choices=[
        ('ACCEPTED', 'ACCEPTED'),
        ('MODIFICATION REQUESTED', 'MODIFICATION REQUESTED'),
        ('PENDING', 'PENDING')],)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sale-{self.sale_id}"

class QuotationItem(BaseModel):
    quotation = models.ForeignKey(Quotation, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity}"


# ─────────────────────────────────────────────────────────────────────────────
# ADD THIS to dash/models.py  (create the file if it doesn't exist)
# ─────────────────────────────────────────────────────────────────────────────

from django.db import models
from django.contrib.auth.models import User


