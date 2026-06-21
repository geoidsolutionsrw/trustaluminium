from django.shortcuts import render, redirect,get_object_or_404
from .forms import addProductForm, editProductForm,addCustomerForm,addSupplierForm,editSupplierForm,editCustomerForm
from .models import  Product, Supplier, Customer, Stock
from sale.models import Sale, SaleItem
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required,permission_required
from django.http import HttpResponse
import pandas as pd
from django.conf import settings
# Dash libraries
from django.db import transaction
import json
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse

   
# ---------- Create supplier viw -----------------------------------
@login_required(login_url="/login")
def supplier(request):
    Suppliers = Supplier.objects.all()
    return render(request,'people/supplierlist.html',{'Suppliers':Suppliers})
@login_required
@require_http_methods(["GET", "POST"])          
def addsupplier(request):
    if request.method == 'POST':
        form = addSupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('/supplier')  # Adjust 'product_list' to your actual product list view name
    else:
        form = addSupplierForm()
    
    return render(request, 'people/addsupplier.html', {'form': form})  
# ------------------Edit supplier----------------------------------
def editsupplier(request, pk):
    suppliers = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        form = editSupplierForm(request.POST, instance=suppliers)
        if form.is_valid():
            form.save()
            return redirect('supplier')
    else:
        form = editSupplierForm(instance=suppliers)
    
    return render(request, 'people/editsupplier.html', {'form': form})
# -----------------Delete------------
@login_required
def deletesupplier(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'GET':
        obj.delete()
        messages.success(request, 'Item deleted successfully.')
        return redirect('supplier')

#  ************************************************************************************************addsupplier
@login_required
def customer(request):
    Customers = Customer.objects.all()
    return render(request,'people/customerlist.html',{'Customers':Customers})
@login_required
@require_http_methods(["GET", "POST"])          
def addcustomer(request):
    if request.method == 'POST':
        form = addCustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('/customer')  # Adjust 'product_list' to your actual product list view name
    else:
        form = addCustomerForm()
    
    return render(request, 'people/addcustomer.html', {'form': form})  
# ------------------Edit supplier----------------------
@login_required
def editcustomer(request, pk):
    Customers = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = editCustomerForm(request.POST, instance=Customers)
        if form.is_valid():
            form.save()
            return redirect('customer')
    else:
        form = editCustomerForm(instance=Customers)
    
    return render(request, 'people/editcustomer.html', {'form': form})
# -----------------Delete------------
@login_required
def deletecustomer(request, pk):
    obj = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'GET':
        obj.delete()
        messages.success(request, 'Item deleted successfully.')
        return redirect('customer')

#  **********************************************/ Product /**************************************************
@login_required
@require_http_methods(["GET", "POST"])               
def addproduct(request):
    if request.method == 'POST':
        form = addProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.creator = request.user
            product.save()
            return redirect('productlist')
    else:
        form = addProductForm()
    return render(request, 'home/product/addproduct.html', {'form': form})
@login_required
def productlist(request):
    # Get all the dataframes
    stock = pd.DataFrame(list(Stock.objects.all().values('product_id', 'stock_quantity')))
    sale_item = pd.DataFrame(list(SaleItem.objects.all().values('product_id', 'quantity')))
    users = pd.DataFrame(list(User.objects.all().values('username', 'id')))
    products_df = pd.DataFrame(list(Product.objects.all().values(
        'productid', 'product_name', 'brand', 'price', 'quantity', 'image', 'creator_id'
    )))

    # Handle stock quantities - fill with 0 for missing products
    if stock.empty:
        stock_qty = pd.DataFrame(columns=['product_id', 'stock_quantity'])
    else:
        stock_qty = stock.groupby('product_id')['stock_quantity'].sum().reset_index()

    # Handle sale quantities - fill with 0 for missing products
    if sale_item.empty:
        sale_qty = pd.DataFrame(columns=['product_id', 'quantity'])
    else:
        sale_qty = sale_item.groupby('product_id')['quantity'].sum().reset_index()

    # Create stock balance with outer join to include all products
    stock_balance = stock_qty.merge(
        sale_qty,
        on='product_id',
        how='outer'  # Changed to outer join
    )

    # Fill NaN values with 0 before calculation
    stock_balance['stock_quantity'] = stock_balance['stock_quantity'].fillna(0)
    stock_balance['quantity'] = stock_balance['quantity'].fillna(0)
    stock_balance['stock'] = stock_balance['stock_quantity'] - stock_balance['quantity']

    # Merge all information together
    products_mrf = products_df.merge(
        users,
        left_on='creator_id',
        right_on='id',
        how='left'
    ).merge(
        stock_balance[['product_id', 'stock']],  # Only keep necessary columns
        left_on='productid',
        right_on='product_id',
        how='left'  # Changed to left join to keep all products
    )

    # Fill any remaining NaN values in stock column with 0
    products_mrf['stock'] = products_mrf['stock'].fillna(0)

    # Handle image paths
    products_mrf['image'] = products_mrf['image'].apply(
        lambda x: '/media/' + str(x) if pd.notna(x) and str(x) != '' else None
    )

    # Select and order final columns
    products = products_mrf[['productid', 'username', 'product_name', 'brand', 'price', 'stock', 'image']]

    context = {
        "products": products.to_dict('records')
    }
    return render(request, 'home/product/productlist.html', context)

@login_required    
def editproduct(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = editProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('productlist')
    else:
        form = editProductForm(instance=product)
    
    return render(request, 'home/product/editproduct.html', {'form': form})
@login_required
def delete_view(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    
    if request.method == 'GET':
        obj.delete()
        messages.success(request, 'Item deleted successfully.')
        return redirect('productlist')

# ----------------------Product Detail ------------------------
@login_required
def product_detail(request,pk):
    prodetail = get_object_or_404(Product, pk=pk)
    return render(request, 'home/product/product_details.html',{'prodetail':prodetail})


# ------------------------- add stock ------------------------------
@login_required
def add_stock(request):
    if request.method == 'POST':
        try:
            stock_items = json.loads(request.POST.get('stock_items', '[]'))
            
            for item in stock_items:
                product_id = item.get('product_id')
                quantity = item.get('quantity')
                
                if product_id and quantity:
                    Stock.objects.create(
                        product_id=product_id,
                        stock_quantity=quantity,
                        creator=request.user
                    )
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    products = Product.objects.all()
    context = {
        'products': products,}
    
    
    return render(request, 'home/product/add_stock.html',context)
