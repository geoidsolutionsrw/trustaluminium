from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponseNotAllowed
from django.db import transaction
from product.models import Customer
from product.models import Product,Stock
from sale.models import Sale, SaleItem
from .models import Quotation, QuotationItem
import json
from django.conf import settings
from django.db.models import OuterRef, Subquery
from django.views.decorators.http import require_http_methods
from decimal import Decimal
from datetime import datetime
import pandas as pd
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.contrib import messages
# views.py
from django.http import HttpResponse
from django.template.loader import get_template,render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from playwright.sync_api import sync_playwright
from django.template.loader import render_to_string


login_required
def add_quotation(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
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
                    
                    # if requested_quantity > available_stock:
                        # raise ValueError(f'Insufficient stock for {item["name"]}. Available: {available_stock}')
                
                # Calculate totals
                total_amount = sum(
                    float(item['price']) * int(item['quantity']) * (1 + float(item['tax'])/100)
                    for item in products_data
                )
                
                # Create Quotation
                quotation = Quotation.objects.create(
                    customer_id=data['customer'],
                    date=data['quotation_date'],
                    total_amount=total_amount,
                    quotation_status=data['quotation_status'],
                    creator=request.user
                )
                
                # Create Quotation items
                for item in products_data:
                    product = Product.objects.get(productid=item['id'])
                    
                    QuotationItem.objects.create(
                        quotation=quotation,
                        product=product,
                        quantity=item['quantity'],
                        price=item['price'],
                        tax=item['tax'],
                        subtotal=item['subtotal']
                    )
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': f'/quotation/{quotation.quo_id}/'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # GET request - render form
    customers = Customer.objects.all()
    products = Product.objects.all()  # No stock filter needed now
    
    context = {
        'customers': customers,
        'products': products,
    }
    return render(request, 'quotation/add_quotation.html', context)

# ===================== Quotation =================================


@login_required
def quotation_list(request):
    quotation_df = pd.DataFrame(list(
        Quotation.objects.all()
        .values('customer_id', 'creator_id', 'quotation_status', 'date', 'total_amount', 'quo_id')
        .order_by('-date')   # ← newest first
    ))

    if quotation_df.empty:
        context = {
            'quotations_data': [],
            'customers':       Customer.objects.all(),
            'products':        Product.objects.all(),
            'current_datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        }
        return render(request, 'quotation/quotation_list.html', context)

    customers_df = pd.DataFrame(list(
        Customer.objects.all().values('cust_id', 'customer_name', 'tin', 'phone_number')
    ))
    users_df = pd.DataFrame(list(
        User.objects.all().values('username', 'id')
    ))

    merged_df = quotation_df.merge(
        customers_df, left_on='customer_id', right_on='cust_id', how='left'
    ).merge(
        users_df, left_on='creator_id', right_on='id', how='left'
    )

    result_df = merged_df[[
        'customer_id', 'username', 'date',
        'customer_name', 'tin', 'phone_number',
        'total_amount', 'quotation_status', 'quo_id'
    ]].fillna('')   # ← cleans up NaN → empty string

    context = {
        'quotations_data':  result_df.to_dict('records'),
        'customers':        Customer.objects.all(),          # ← for edit modal
        'products':         Product.objects.all(),           # ← for edit modal
        'current_datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    }
    return render(request, 'quotation/quotation_list.html', context)

# ─────────────────────────────────────────────────────────────────────────────
# Update quotation_detail in quotation/views.py
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def quotation_detail(request, pk):
    quotationdetail = get_object_or_404(Quotation, pk=pk)
    quotationitem   = QuotationItem.objects.filter(quotation=quotationdetail)
    return render(request, 'quotation/quotation-details.html', {
        'quotationdetail': quotationdetail,
        'quotationitem':   quotationitem,
        'customers':       Customer.objects.all().order_by('customer_name'),
        'products':        Product.objects.all().order_by('product_name'),
    })

# ------------------------------ Delete quotation --------------------------
@login_required
def delete_quotation(request, pk):
    if request.method == 'POST':
        quotation = get_object_or_404(Quotation, quo_id=pk)
        quotation.delete()
        messages.success(request, 'Quotation deleted successfully')
        return redirect('quotation_list')
    return HttpResponseNotAllowed(['POST'])  
# ------------------------------ Printing pdf--------------------------------


@login_required
# def export_quotation_pdf(request, pk):
#     # Get the quotation detail object
#     quotationdetail = get_object_or_404(Quotation, pk=pk)
#     quotationitem = QuotationItem.objects.filter(quotation=quotationdetail)
    
#     # Prepare the context
#     context = {
#         'quotationdetail': quotationdetail,
#         'quotationitem': quotationitem,
#     }
    
#     # Get the template
#     template = get_template('quotation/quotation_pdf.html')
    
#     # Render the template
#     html = template.render(context)
    
#     # Create a file-like buffer to receive PDF data
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="quotation_{pk}.pdf"'
    
#     # Create PDF
#     pisa_status = pisa.CreatePDF(
#         html, dest=response,
#         encoding='utf-8')
    
#     # Return response
#     if pisa_status.err:
#         return HttpResponse('We had some errors with creating the PDF <pre>' + html + '</pre>')
#     return response

@login_required
def export_quotation_pdf(request, pk):
    quotationdetail = get_object_or_404(Quotation, pk=pk)
    quotationitem   = QuotationItem.objects.filter(quotation=quotationdetail)

    html_string = render_to_string('quotation/quotation_pdf.html', {
        'quotationdetail': quotationdetail,
        'quotationitem':   quotationitem,
    })

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page    = browser.new_page()
        page.set_content(html_string, wait_until='networkidle')
        pdf_bytes = page.pdf(
            format='A4',
            print_background=True,
            margin={
                'top':    '15mm',
                'bottom': '15mm',
                'left':   '15mm',
                'right':  '15mm',
            },
            display_header_footer=False,   # ← removes header/footer
        )
        browser.close()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quotation_{pk}.pdf"'
    return response
# ─────────────────────────────────────────────────────────────────────────────
# ADD THIS to quotation/views.py
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def edit_quotation(request, pk):
    """
    GET  → returns quotation data as JSON (for modal prefill)
    POST → saves the edited quotation and items
    """
    quotation = get_object_or_404(Quotation, quo_id=pk)

    # ── GET: return JSON for modal ─────────────────────────────────────────
    if request.method == 'GET':
        items = QuotationItem.objects.filter(quotation=quotation).select_related('product')
        data = {
            'quo_id':           quotation.quo_id,
            'customer_id':      quotation.customer_id,
            'customer_name':    quotation.customer.customer_name,
            'date':             quotation.date.strftime('%Y-%m-%d'),
            'quotation_status': quotation.quotation_status,
            'total_amount':     str(quotation.total_amount),
            'items': [{
                'item_id':      item.id,
                'product_id':   item.product.productid,
                'product_name': item.product.product_name,
                'quantity':     item.quantity,
                'price':        str(item.price),
                'tax':          str(item.tax),
                'subtotal':     str(item.subtotal),
            } for item in items]
        }
        return JsonResponse({'success': True, 'quotation': data})

    # ── POST: save changes ─────────────────────────────────────────────────
    if request.method == 'POST':
        try:
            with transaction.atomic():
                products_data     = json.loads(request.POST.get('products', '[]'))
                quotation_status  = request.POST.get('quotation_status', quotation.quotation_status)
                quotation_date    = request.POST.get('quotation_date', '')
                customer_id       = request.POST.get('customer', quotation.customer_id)

                if not products_data:
                    return JsonResponse({'success': False, 'error': 'No products added.'})

                # Recalculate total
                total_amount = sum(
                    float(item['price']) * int(item['quantity']) * (1 + float(item.get('tax', 0)) / 100)
                    for item in products_data
                )

                # Update quotation header
                quotation.customer_id      = customer_id
                quotation.quotation_status = quotation_status
                quotation.total_amount     = total_amount
                if quotation_date:
                    quotation.date = quotation_date
                quotation.save()

                # Replace all items
                QuotationItem.objects.filter(quotation=quotation).delete()
                for item in products_data:
                    product = Product.objects.get(productid=item['id'])
                    QuotationItem.objects.create(
                        quotation = quotation,
                        product   = product,
                        quantity  = item['quantity'],
                        price     = item['price'],
                        tax       = item.get('tax', 0),
                        subtotal  = item['subtotal'],
                    )

                return JsonResponse({
                    'success':      True,
                    'redirect_url': f'/quotation/{quotation.quo_id}/',
                    'message':      f'Quotation #{quotation.quo_id} updated successfully.',
                })

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid method.'})