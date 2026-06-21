from django.contrib import admin
from django.urls import path
# from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('addproduct', views.addproduct,name='addproduct'),
    path('productlist', views.productlist,name='productlist'),
    path('add_stock', views.add_stock, name='add_stock'),
    path('editproduct/<int:pk>/', views.editproduct, name='editproduct'),
    path('delete/<int:pk>/', views.delete_view, name='delete_item'),
    path('supplier', views.supplier, name='supplier'),
    path('customer', views.customer, name='customer'),
    path('addcustomer', views.addcustomer, name='addcustomer'),
    path('editcustomer/<int:pk>/', views.editcustomer, name='editcustomer'),
    path('deletecustomer/<int:pk>/', views.deletecustomer, name='deletecustomer'),
    path('addsupplier', views.addsupplier, name='addsupplier'),
    path('editsupplier/<int:pk>/', views.editsupplier, name='editsupplier'),
    path('deletesupplier/<int:pk>/', views.deletesupplier, name='deletesupplier'),
    path('product_detail/<int:pk>/', views.product_detail, name='product_detail'),
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)