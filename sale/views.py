# sales/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from product.models import Customer
from product.models import Product,Stock
from .models import Sale, SaleItem, Payment
from django.http import JsonResponse,HttpResponseNotAllowed
from django.http import HttpResponse
import json
from .forms import SaleForm, SaleItemForm, PaymentForm,CreatePaymentForm
from django.conf import settings
from django.db.models import OuterRef, Subquery
from django.views.decorators.http import require_http_methods
from decimal import Decimal
from datetime import datetime
import pandas as pd
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.shortcuts import render
from django.db.models.functions import Coalesce
from django.db.models import F, Sum, Value, IntegerField, CharField, Case, When,DecimalField
from django.db.models.functions import Coalesce
from django.db.models import ExpressionWrapper
# the time
from datetime import datetime, timedelta
from django.utils import timezone

@login_required
@login_required
def saleslist(request):
    today     = timezone.now()
    yesterday = today - timedelta(days=1)
 
    # ── Fast KPI indicators using simple aggregates ──────────────────────
    paid_sales_today      = Payment.objects.filter(
        sale__date__date=today.date()
    ).aggregate(total=Sum('paid_amount'))['total'] or 0
 
    paid_sales_yesterday  = Payment.objects.filter(
        sale__date__date=yesterday.date()
    ).aggregate(total=Sum('paid_amount'))['total'] or 0
 
    total_expected_amount = Sale.objects.filter(
        date__date=today.date()
    ).aggregate(total=Sum('total_amount'))['total'] or 0
 
    balance_sales = total_expected_amount - paid_sales_today
 
    # ── Fast sales list using pandas (same approach as productlist) ──────
    sales_df = pd.DataFrame(list(
        Sale.objects.all()
        .values('sale_id', 'customer_id', 'date', 'total_amount', 'payment_status', 'creator_id')
        .order_by('-date')                     # ← newest first
    ))
 
    if sales_df.empty:
        context = {
            'sales_data':            [],
            'products':              Product.objects.values('productid', 'product_name').order_by('product_name'),
            'total_expected_amount': total_expected_amount,
            'paid_sales_today':      paid_sales_today,
            'balance_sales':         balance_sales,
            'paid_sales_yesterday':  paid_sales_yesterday,
        }
        return render(request, 'sale/saleslist.html', context)
 
    # Payments aggregated per sale
    payments_df = pd.DataFrame(list(
        Payment.objects.values('sale_id')
        .annotate(paid_amount=Sum('paid_amount'))
        .values('sale_id', 'paid_amount')
    ))
 
    # Customers
    customers_df = pd.DataFrame(list(
        Customer.objects.values('cust_id', 'customer_name', 'tin', 'phone_number')
    ))
 
    # Users
    users_df = pd.DataFrame(list(
        User.objects.values('id', 'username')
    ))
 
    # Merge
    merged = sales_df.merge(
        customers_df, left_on='customer_id', right_on='cust_id', how='left'
    ).merge(
        users_df, left_on='creator_id', right_on='id', how='left'
    )
 
    if not payments_df.empty:
        merged = merged.merge(payments_df, on='sale_id', how='left')
    else:
        merged['paid_amount'] = 0
 
    merged['paid_amount']  = merged['paid_amount'].fillna(0)
    merged['balance']      = merged['total_amount'] - merged['paid_amount']
    merged['payment_completion'] = merged.apply(
        lambda r: 'Complete' if r['total_amount'] == r['paid_amount'] else 'Incomplete',
        axis=1
    )
    merged = merged.fillna('')
 
    # Select final columns
    result = merged[[
        'sale_id', 'date', 'customer_name', 'tin',
        'payment_status', 'total_amount', 'paid_amount',
        'balance', 'payment_completion', 'username'
    ]]
 
    context = {
        'sales_data':            result.to_dict('records'),
        'products':              Product.objects.values('productid', 'product_name').order_by('product_name'),
        'total_expected_amount': total_expected_amount,
        'paid_sales_today':      paid_sales_today,
        'balance_sales':         balance_sales,
        'paid_sales_yesterday':  paid_sales_yesterday,
    }
    return render(request, 'sale/saleslist.html', context)
# ******************************************************   ***************
login_required
def addsales1(request):
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                data = request.POST
                products_data = json.loads(data.get('products', '[]'))
                
                if not products_data:
                    return JsonResponse({'success': False, 'error': 'No products added'})
                
                # Calculate totals
                total_amount = sum(
                    float(item['price']) * int(item['quantity']) * (1 + float(item['tax'])/100)
                    for item in products_data
                )
                
                # Create sale
                sale = Sale.objects.create(
                    customer_id=data['customer'],
                    date=data['sale_date'],
                    total_amount=total_amount,
                    paid_amount=0,  # Initial paid amount
                    payment_status=data['payment_status'],
                    creator=request.user
                )
                
                # Create sale items
                for item in products_data:
                    product = Product.objects.get(productid=item['id'])
                    
                    # Check stock
                    if product.quantity < int(item['quantity']):
                        raise ValueError(f'Insufficient stock for {product.product_name}')
                    
                    # Create sale item
                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=item['quantity'],
                        price=item['price'],
                        tax=item['tax'],
                        subtotal=item['subtotal']
                    )
                    
                    # Update stock
                    product.quantity -= int(item['quantity'])
                    product.save()
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': f'/sales/{sale.sale_id}/'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # GET request - render form
    customers = Customer.objects.all()
    products = Product.objects.filter(quantity__gt=0)  # Only show products with stock
    
    context = {
        'customers': customers,
        'products': products,
    }
    return render(request, 'sale/add-sales.html', context)
login_required
@transaction.atomic
def addsales(request):
    if request.method == 'POST':
        try:
            data = request.POST
            products_data = json.loads(data.get('products', '[]'))
            
            if not products_data:
                return JsonResponse({'success': False, 'error': 'No products added'})
            
            # Stock availability check with aggregation
            for item in products_data:
                product_id = item['id']
                requested_quantity = int(item['quantity'])
                
                # Calculate available stock
                total_stock = Stock.objects.filter(product_id=product_id).aggregate(
                    total_stock=Sum('stock_quantity')
                )['total_stock'] or 0
                
                sold_quantity = SaleItem.objects.filter(product_id=product_id).aggregate(
                    total_sold=Sum('quantity')
                )['total_sold'] or 0
                
                available_stock = total_stock - sold_quantity
                
                if requested_quantity > available_stock:
                    return JsonResponse({
                        'success': False,
                        'error': f'Insufficient stock for {item["name"]}. Available: {available_stock}'
                    })
            
            # Calculate totals
            total_amount = sum(
                float(item['price']) * int(item['quantity']) * (1 + float(item['tax'])/100)
                for item in products_data
            )
            
            # Get payment data
            payment_status = data.get('payment_status')
            paid_amount = data.get('payment_amount', 0)  # Changed from paid_amount to payment_amount
            
            # Validate payment amount
            if payment_status == 'FULL' and float(paid_amount) != total_amount:
                return JsonResponse({
                    'success': False,
                    'error': 'Full payment amount must equal total amount'
                })
            elif payment_status == 'PARTIAL' and float(paid_amount) > total_amount:
                return JsonResponse({
                    'success': False,
                    'error': 'Partial payment cannot exceed total amount'
                })
            
            # Create sale
            sale = Sale.objects.create(
                customer_id=data['customer'],
                date=data['sale_date'],
                total_amount=total_amount,
                payment_status=payment_status,
                creator=request.user
            )
            
            # Create sale items
            for item in products_data:
                product = Product.objects.get(productid=item['id'])
                
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price'],
                    tax=item['tax'],
                    subtotal=item['subtotal']
                )
            
            # Create payment only if amount is greater than 0
            if float(paid_amount) > 0:
                Payment.objects.create(
                    sale=sale,
                    paid_amount=paid_amount,
                    creator=request.user
                )
            
            return JsonResponse({
                'success': True,
                'redirect_url': f'/sales/{sale.sale_id}/'
            })
            
        except Product.DoesNotExist as e:
            return JsonResponse({
                'success': False,
                'error': 'Product not found'
            })
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        except Exception as e:
            # Log the actual error for debugging
            print(f"Error creating sale: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while processing the sale. Please check all inputs and try again.'
            })
    
    # GET request - render form
    form = SaleForm()
    customers = Customer.objects.all()
    products = Product.objects.all()
    
    context = {
        'form': form,
        'customers': customers,
        'products': products,
    }
    return render(request, 'sale/add-sales.html', context)
# ------------------------------------------- get stoc --------------
@login_required
def get_available_stock(request, product_id):
    total_stock = Stock.objects.filter(product_id=product_id).aggregate(
        total_stock=Sum('stock_quantity')
    )['total_stock'] or 0
    
    sold_quantity = SaleItem.objects.filter(product_id=product_id).aggregate(
        total_sold=Sum('quantity')
    )['total_sold'] or 0
    
    available_stock = total_stock - sold_quantity
    
    return JsonResponse({
        'available_stock': available_stock
    })
# -------------------------------------------------------------------------------

@login_required
def sale_detail(request, pk):
    saledetail = get_object_or_404(Sale, pk=pk)
    saleitems  = SaleItem.objects.filter(sale=saledetail)
    return render(request, 'sale/sales-details.html', {
        'saledetail': saledetail,
        'saleitems':  saleitems,
        'customers':  Customer.objects.all().order_by('customer_name'),
        'products':   Product.objects.all().order_by('product_name'),
    })
def addtest(request, pk):
    if request.method == "POST":
        try:
            # Get form data
            customer_id = request.POST.get('customer')
            sale_date = request.POST.get('sale_date')
            status = request.POST.get('status')
            products_json = request.POST.get('products')

            # Validate products data
            if not products_json:
                return JsonResponse({'success': False, 'error': 'No products added to sale'})

            products_data = json.loads(products_json)

            # Fetch existing sale
            sale = Sale.objects.get(pk=pk)

            # Reset sale totals
            sale.total_amount = Decimal('0.00')
            sale.total_tax = Decimal('0.00')
            sale.save()

            # Clear existing sale items
            sale.saleitem_set.all().delete()

            total_amount = Decimal('0.00')
            total_tax = Decimal('0.00')

            # Process each product
            for item in products_data:
                product = Product.objects.get(id=item['productid'])
                quantity = int(item['quantity'])

                # Validate stock availability
                if product.quantity < quantity:
                    return JsonResponse({
                        'success': False,
                        'error': f'Insufficient stock for {product.product_name}'
                    })

                # Calculate amounts
                price = Decimal(str(item['price']))
                tax_rate = Decimal(str(item['tax']))
                subtotal = price * quantity
                tax_amount = (subtotal * tax_rate) / Decimal('100.00')

                # Create sale item
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price=price,
                    tax_rate=tax_rate,
                    tax_amount=tax_amount,
                    subtotal=subtotal
                )

                # Update product quantity
                product.quantity -= quantity
                product.save()

                # Update sale totals
                total_amount += subtotal
                total_tax += tax_amount

            # Finalize sale totals
            sale.total_amount = total_amount
            sale.total_tax = total_tax
            sale.status = status
            sale.sale_date = sale_date
            sale.customer_id = customer_id
            sale.save()

            return JsonResponse({
                'success': True,
                'redirect_url': f'/sales/{sale.sale_id}/'
            })

        except Sale.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Sale not found'})

        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})

        except ValueError as e:
            return JsonResponse({'success': False, 'error': f'Invalid data: {str(e)}'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': f'An unexpected error occurred: {str(e)}'})

    # Handle GET request - render form
    try:
        sale = Sale.objects.get(pk=pk)
        context = {
            'sale': sale,
            'customers': Customer.objects.all(),
            'products': Product.objects.all()
        }
        return render(request, 'sale/edit-sales.html', context)

    except Sale.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sale not found'})

#  EDIT SALES
@login_required
def get_sale_for_edit(request, pk):
    """
    GET → returns sale data as JSON for modal prefill
    """
    sale      = get_object_or_404(Sale, pk=pk)
    saleitems = SaleItem.objects.filter(sale=sale).select_related('product')
 
    data = {
        'sale_id':        sale.sale_id,
        'customer_id':    sale.customer_id,
        'customer_name':  sale.customer.customer_name,
        'date':           sale.date.strftime('%Y-%m-%d'),
        'payment_status': sale.payment_status,
        'total_amount':   str(sale.total_amount),
        'items': [{
            'product_id':   item.product.productid,
            'product_name': item.product.product_name,
            'quantity':     item.quantity,
            'price':        str(item.price),
            'tax':          str(item.tax),
            'subtotal':     str(item.subtotal),
        } for item in saleitems]
    }
    return JsonResponse({'success': True, 'sale': data})
 

@login_required

def edit_sales(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
 
    # ── GET: if AJAX return JSON, else render full page form ──────────────
    if request.method == 'GET':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return get_sale_for_edit(request, pk)
        # Non-AJAX GET → render full page (fallback)
        customers      = Customer.objects.all()
        products       = Product.objects.all()
        sale_items     = sale.items.select_related('product')
        existing_products = json.dumps([{
            'id':       item.product.productid,
            'name':     item.product.product_name,
            'quantity': item.quantity,
            'price':    float(item.price),
            'tax':      float(item.tax),
            'subtotal': float(item.subtotal),
        } for item in sale_items])
        return render(request, 'sale/edit-sales.html', {
            'sale':               sale,
            'customers':          customers,
            'products':           products,
            'existing_products':  existing_products,
        })
 
    # ── POST: save changes ─────────────────────────────────────────────────
    if request.method == 'POST':
        try:
            with transaction.atomic():
                data          = request.POST
                products_data = json.loads(data.get('products', '[]'))
 
                if not products_data:
                    return JsonResponse({'success': False, 'error': 'No products provided.'})
 
                # Recalculate total
                total_amount = sum(float(p.get('subtotal', 0)) for p in products_data)
 
                # Update sale header
                sale.customer_id     = data.get('customer', sale.customer_id)
                sale.date            = data.get('sale_date', sale.date)
                sale.total_amount    = total_amount
                sale.payment_status  = data.get('payment_status', sale.payment_status)
                sale.save()
 
                # Replace items
                sale.items.all().delete()
                for item in products_data:
                    product = Product.objects.get(productid=item['id'])
                    SaleItem.objects.create(
                        sale     = sale,
                        product  = product,
                        quantity = item['quantity'],
                        price    = item['price'],
                        tax      = item.get('tax', 0),
                        subtotal = item['subtotal'],
                    )
 
                return JsonResponse({
                    'success':      True,
                    'redirect_url': f'/sales/{sale.sale_id}/',
                    'message':      f'Sale #{sale.sale_id} updated successfully.',
                })
 
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': str(e)})
 
    return JsonResponse({'success': False, 'error': 'Invalid method.'})

@login_required
def payment_approval(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        try:
            # Only update the editable fields
            sale.total_amount = request.POST.get('total_amount')
            sale.payment_status = request.POST.get('payment_status')
            sale.save()
            
            messages.success(request, 'Payment details updated successfully')
            return redirect('sale_list')  # Replace with your actual sale list URL name
        except Exception as e:
            messages.error(request, f'Error updating payment: {str(e)}')
    
    return redirect('saleslist')
#  =========================   Delete sales view ====================================
@login_required
def delete_sale(request, sale_id):
    if request.method == 'POST':
        try:
            sale = Sale.objects.get(sale_id=sale_id)
            sale.delete()
            return JsonResponse({'success': True})
        except Sale.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Sale not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# ----------------------------------- Export pdf --------------------------------
@login_required
def export_sale_pdf(request, pk):
    # Get the quotation detail object
    saledetail = get_object_or_404(Sale, pk=pk)
    saleitem = SaleItem.objects.filter(sale=saledetail)
    
    # Prepare the context
    context = {
        'saledetail': saledetail,
        'saleitem': saleitem,
    }
    
    # Get the template
    template = get_template('sale/sale_pdf.html')
    
    # Render the template
    html = template.render(context)
    
    # Create a file-like buffer to receive PDF data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quotation_{pk}.pdf"'
    
    # Create PDF
    pisa_status = pisa.CreatePDF(
        html, dest=response,
        encoding='utf-8')
    
    # Return response
    if pisa_status.err:
        return HttpResponse('We had some errors with creating the PDF <pre>' + html + '</pre>')
    return response
@login_required    
def create_payment(request):
    if request.method == 'POST':
        form = CreatePaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.creator = request.user
            payment.save()
            messages.success(request, 'Payment created successfully!')
            return redirect('saleslist')  # Replace with your URL
    else:
        form = CreatePaymentForm()
    
    context = {
        'form': form,
        'title': 'Create Payment'  # For the template title
    }
    return render(request, 'sale/create_payment.html', context)
