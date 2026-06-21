# forms.py
from django import forms
from .models import Quotation, QuotationItem
from product.models import Customer, Product

class QuotationForm(forms.Form):
    QUOTATION_STATUS = (
        ('ACCEPTED', 'ACCEPTED'),
        ('MODIFICATION REQUESTED', 'MODIFICATION REQUESTED'),
        ('PENDING', 'PENDING'),
    )
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        empty_label="Choose Customer",
        widget=forms.Select(attrs={'class': 'select'})
    )
    quotation_date = forms.DateTimeField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    quotation_status = forms.ChoiceField(

    widget=forms.Select(attrs={'class': 'select'})
    )
    
    paid_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class QuotationItemForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        empty_label="Select Product",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    tax = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )