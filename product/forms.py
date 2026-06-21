from django import forms
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product,Customer,Supplier

# class addProductForm(forms.ModelForm):
#     class Meta:
#         model =Product
#         fields = ['productid', 'product_name','category','brand' ,'price', 'quantity']
class addProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['productid', 'product_name', 'category', 'brand', 'price', 'quantity', 'image']
    def __init__(self, *args, **kwargs):
        super(addProductForm, self).__init__(*args, **kwargs)  
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control' 
        # widgets = {
        #     'image': forms.FileInput(attrs={
        #         'class': 'form-control',
        #         'id': 'product-image'
        #     })
        # }
class editProductForm(forms.ModelForm):
    class Meta:
        model =Product
        fields = ['productid', 'product_name','category','brand' ,'price', 'quantity']
    def __init__(self, *args, **kwargs):
        super(editProductForm, self).__init__(*args, **kwargs)  
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  
            
#  stock add form
class addStock(forms.Form):
    
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        empty_label="Product ",
        widget=forms.Select(attrs={'class': 'select'}))
    stock_quantity=forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
# Supplier
class addSupplierForm(forms.ModelForm):
    class Meta:
        model=Supplier 
        fields =['supplier_id', 'supplier_name','country', 'phone_number','email_address','address','contact_person']
        widgets ={
            'email_address': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
        
# Edit
class editSupplierForm(forms.ModelForm):
    class Meta:
        model=Supplier 
        fields =['supplier_id', 'supplier_name','country', 'phone_number','email_address','address','contact_person']
        widgets ={
            'email_address': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(editSupplierForm, self).__init__(*args, **kwargs)  
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
# ###
class addCustomerForm(forms.ModelForm):
    class Meta:
        model=Customer 
        fields =['cust_id', 'customer_name', 'phone_number','email_address','address','tin','customer_type']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email_address': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'tin': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_type': forms.TextInput(attrs={'class': 'form-control'}),  
            
        }
# Edit
class editCustomerForm(forms.ModelForm):
    class Meta:
        model=Customer 
        fields =['cust_id', 'customer_name', 'phone_number','email_address','address','tin','customer_type']
        widgets ={
            'email_address': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(editCustomerForm, self).__init__(*args, **kwargs)  
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
