from django import forms
from .models import Sale, SaleItem, Payment
from product.models import Product, Customer
from django.db.models import Sum, F,DecimalField as DbDecimalField, Value
from django.db.models.functions import Coalesce
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'date', 'payment_status', 'notes']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'payment_status': forms.Select(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'price', 'tax']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'tax': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['paid_amount', 'notes']
        widgets = {
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
class CreatePaymentForm(forms.ModelForm):
    # Add sale as ModelChoiceField instead of using the default field
    sale = forms.ModelChoiceField(
        queryset=None,  # We'll set this in __init__
        empty_label="Select a Sale",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get sales with remaining balance
        sales_with_balance = Sale.objects.annotate(
            paid_total=Coalesce(
                Sum('payments__paid_amount'),
                Value(0),
                output_field=DbDecimalField()
            ),
            balance=F('total_amount') - F('paid_total')
        ).filter(
            balance__gt=0
        )
        
        # Set the queryset for the sale field
        self.fields['sale'].queryset = sales_with_balance
        
        # Customize the display of each sale option
        self.fields['sale'].label_from_instance = lambda obj: (
            f"Sale {obj.sale_id} - {obj.customer.customer_name} "
            f"(Balance: {obj.balance})"
        )

        # Style the other fields
        self.fields['paid_amount'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter amount'
        })
        self.fields['notes'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter notes (optional)'
        })

    class Meta:
        model = Payment
        fields = ['sale', 'paid_amount', 'notes']