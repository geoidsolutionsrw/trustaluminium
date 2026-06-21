from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('quotation/edit/<int:pk>/', views.edit_quotation, name='edit_quotation'),
    path('quotation_list', views.quotation_list,name='quotation_list'),
    path('add_quotation', views.add_quotation,name='add_quotation'),
    # path('addtest/<int:pk>/', views.addtest,name='addtest'),
    # path('sale_detail/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('quotation/<int:pk>/', views.quotation_detail, name='quotation_detail'),
    path('quotation/export-pdf/<int:pk>/', views.export_quotation_pdf, name='export_quotation_pdf'),
    path('quotation/delete/<int:pk>/', views.delete_quotation, name='delete_quotation'),
    # # addtest
    # path('edit_sales/<int:pk>/', views.edit_sales, name='edit_sales'),
    # path('payment_approval/<int:pk>/', views.payment_approval, name='payment_approval'),
    # path('delete_sale/<str:sale_id>/', views.delete_sale, name='delete_sale'),
    # path('get-available-stock/<int:product_id>/', views.get_available_stock, name='get_available_stock'),
    # path('addsales1', views.addsales1,name='addsales1'),
]