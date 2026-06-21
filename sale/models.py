from django.db import models
from django.db import models
from django.contrib.auth.models import User

from product.models import Customer  # Import from customer app
from product.models import Product   # Import from product app
from authentication.models import BaseModel


class Sale(BaseModel):
    PAYMENT_STATUS = (
        ('FULL', 'Full Payment'),
        ('PARTIAL', 'Partial Payment'),
        ('PENDING', 'Pending'),
    )
    PAYMENT_COMPLETION=(
        ('COMPLETE','Complete'),
        ('PENDING','Pending'),
        ('CANCEL','Cancel'),
    )
    
    sale_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=[
        ('FULL', 'Full Payment'),
        ('PARTIAL', 'Partial Payment'),
        ('PENDING', 'Pending')],)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Sale-{self.sale_id}"

class SaleItem(BaseModel):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity}"
    
class Payment(BaseModel):  
    PAYMENT_CHOICES = [
        ('full', 'Full Payment'),
        ('half', 'Half Payment'),
        ('installment', 'Installment'),
    ]
    sale = models.ForeignKey(Sale, related_name='payments', on_delete=models.CASCADE)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)  # New field
    notes = models.TextField(blank=True, null=True)  # New field

    def __str__(self):
        return f"Payment for Sale {self.sale.sale_id} - {self.amount_paid}"

    class Meta:
        db_table = 'payment'

