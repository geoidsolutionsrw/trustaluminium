from django.contrib import admin
from django.urls import path
# from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('homepage', views.homepage,name='homepage'),
    path('home', views.home,name='home'),
    path('sales_report', views.sales_report,name='sales_report'),
    # Export ther dpf, excel, print
    path('sales-report/pdf/', views.sales_report_pdf, name='sales_report_pdf'),
    path('sales-report/excel/', views.sales_report_excel, name='sales_report_excel'),
    path('top_customers', views.top_customers, name='top_customers'),
    path('', views.homepage,name='homepage'),
#     # path('editproduct/<int:productid>/', views.editproduct, name='editproduct'),
#     path('editproduct/<int:pk>/', views.editproduct, name='editproduct'),
#     path('delete/<int:pk>/', views.delete_view, name='delete_item'),
    path('contactus', views.contactus, name='contactus'),
#     path('customer', views.customer, name='customer'),
#     path('addcustomer', views.addcustomer, name='addcustomer'),
#     path('editcustomer/<int:pk>/', views.editcustomer, name='editcustomer'),
#     path('deletecustomer/<int:pk>/', views.deletecustomer, name='deletecustomer'),
#     path('addsupplier', views.addsupplier, name='addsupplier'),
#     path('editsupplier/<int:pk>/', views.editsupplier, name='editsupplier'),
#     path('deletesupplier/<int:pk>/', views.deletesupplier, name='deletesupplier'),
#     path('product_detail/<int:pk>/', views.product_detail, name='product_detail'),
    

    
    
    
    

# ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
]