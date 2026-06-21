from django.contrib import admin
from django.urls import path, reverse_lazy
from . import views
# from authentication.views import ResetPasswordView
from .views import ResetPasswordView, ResetPasswordConfirmView, ResetPasswordCompleteView, ResetPasswordDoneView
from django.contrib.auth import views as auth_views 
urlpatterns = [
    path('adduser', views.adduser,name='adduser'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/assign/', views.assign_user_to_group, name='assign_user_to_group'),
    path('permissions/create/', views.create_custom_permission, name='create_custom_permission'),
    path('users/', views.user_list, name='user_list'),
    path('permissions/', views.permission_list, name='permission_list'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    
    
     path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

# #     path('groups/<int:group_id>/permissions/', views.manage_group_permissions, name='manage_group_permissions'),
#     path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
#     path('password-reset/done/', ResetPasswordDoneView.as_view(), name='password_reset_done'),
#     path('password-reset-confirm/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='password_reset_confirm'),
#     path('password-reset-complete/', ResetPasswordCompleteView.as_view(), name='password_reset_complete'),


]