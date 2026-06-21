from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from . import views

# app_name = 'sale'
urlpatterns = [
    path('saleslist', views.saleslist,name='saleslist'),
    path('addsales/', views.addsales,name='addsales'),
    path('addtest/<int:pk>/', views.addtest,name='addtest'),
    path('sale_detail/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    # addtest
    path('edit_sales/<int:pk>/', views.edit_sales, name='edit_sales'),
    path('payment_approval/<int:pk>/', views.payment_approval, name='payment_approval'),
    path('delete_sale/<str:sale_id>/', views.delete_sale, name='delete_sale'),
    path('get-available-stock/<int:product_id>/', views.get_available_stock, name='get_available_stock'),
    path('addsales1', views.addsales1,name='addsales1'),
    path('sale/export-pdf/<int:pk>/', views.export_sale_pdf, name='export_sale_pdf'),
    path('create_payment/', views.create_payment, name='create_payment'),
]