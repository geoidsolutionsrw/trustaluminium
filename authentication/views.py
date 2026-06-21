from django.shortcuts import render, redirect,get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login
from .forms import RegisterForm
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import User, Group, Permission
from django.contrib.admin.models import LogEntry, DELETION
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.core.paginator import Paginator
from django.apps import apps
from django.db import models
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetDoneView
from django.contrib.messages.views import SuccessMessageMixin


@permission_required('auth.add_user')
def adduser(request):
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('productlist')

    else:
        form = RegisterForm()
    
    return render(request, 'registration/adduser.html', {'form': form})




class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = '/registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                     "if an account exists with the email you entered. You should receive them shortly." \
                     " If you don't receive an email, " \
                     "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('password_reset_done')

class ResetPasswordConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class ResetPasswordCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'

class ResetPasswordDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'
 
#  =============== create group ===========
@permission_required('auth.add_group')
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        permissions = request.POST.getlist('permissions')
        
        # Create new group
        group = Group.objects.create(name=group_name)
        
        # Add selected permissions to group
        for perm_id in permissions:
            permission = Permission.objects.get(id=perm_id)
            group.permissions.add(permission)
        
        messages.success(request, f'Group {group_name} created successfully')
        return redirect('group_list')
        
    # Get all available permissions
    permissions = Permission.objects.all()
    return render(request, 'registration/auth/create_group.html', {'permissions': permissions})

@permission_required('auth.change_group')
def assign_user_to_group(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        group_ids = request.POST.getlist('groups')
        
        user = User.objects.get(id=user_id)
        # Clear existing groups and add new ones
        user.groups.clear()
        for group_id in group_ids:
            group = Group.objects.get(id=group_id)
            user.groups.add(group)
            
        messages.success(request, f'Groups updated for {user.username}')
        return redirect('user_list')
        
    users = User.objects.all()
    groups = Group.objects.all()
    return render(request, 'registration/auth/assign_group.html', {
        'users': users,
        'groups': groups
    })

@permission_required('auth.add_permission')
def create_custom_permission(request):
    if request.method == 'POST':
        codename = request.POST.get('codename')
        name = request.POST.get('name')
        content_type = ContentType.objects.get(
            app_label='yourapp',
            model='yourmodel'
        )
        
        Permission.objects.create(
            codename=codename,
            name=name,
            content_type=content_type
        )
        messages.success(request, f'Permission {name} created successfully')
        return redirect('permission_list')
        
    return render(request, 'registration/create_permission.html')

@login_required
@permission_required('auth.view_user')
def user_list(request):
    search_query = request.GET.get('search', '')
    
    # Filter users based on search query
    users = User.objects.all()
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Add group information
    users = users.prefetch_related('groups')
    
    # Pagination
    paginator = Paginator(users, 10)  # 10 users per page
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    return render(request, 'registration/userlist.html', {
        'users': users,
        'search_query': search_query
    })

@login_required
@permission_required('auth.view_permission')
def permission_list(request):
    search_query = request.GET.get('search', '')
    
    # Filter permissions based on search query
    permissions = Permission.objects.select_related('content_type')
    if search_query:
        permissions = permissions.filter(
            Q(name__icontains=search_query) |
            Q(codename__icontains=search_query) |
            Q(content_type__app_label__icontains=search_query)
        )
    
    # Group permissions by app
    permissions_by_app = {}
    for perm in permissions:
        app_label = perm.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        permissions_by_app[app_label].append(perm)
    
    return render(request, 'registration/auth/permission_list.html', {
        'permissions_by_app': permissions_by_app,
        'search_query': search_query
    })
#===================== Permission group ================================
@login_required
@permission_required('auth.change_group')
def manage_group_permissions(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        # Get selected permissions from form
        selected_permissions = request.POST.getlist('permissions')
        
        # Clear existing permissions and add new ones
        group.permissions.clear()
        group.permissions.add(*selected_permissions)
        
        messages.success(request, f'Permissions updated for group {group.name}')
        return redirect('group_list')
    
    # Get all available permissions
    all_permissions = Permission.objects.all().select_related('content_type')
    
    # Group permissions by app
    permissions_by_app = {}
    for perm in all_permissions:
        app_label = perm.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        permissions_by_app[app_label].append(perm)
    
    return render(request, 'registration/auth/manage_group_permissions.html', {
        'group': group,
        'permissions_by_app': permissions_by_app
    }) 

# ==== Change user =====
@login_required
@permission_required('auth.change_user')
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # Update user information
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.is_active = 'is_active' in request.POST
        
        # Update password if provided
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        # Update groups
        selected_groups = request.POST.getlist('groups')
        user.groups.clear()
        user.groups.add(*selected_groups)
        
        user.save()
        messages.success(request, f'User {user.username} updated successfully')
        return redirect('user_list')
    
    groups = Group.objects.all()
    return render(request, 'registration/auth/edituser.html', {
        'user_obj': user,
        'groups': groups
    })

@login_required
@permission_required('auth.delete_user')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Prevent self-deletion
    if user == request.user:
        messages.error(request, "You cannot delete your own account")
        return redirect('user_list')
    
    if request.method == 'POST':
        try:
            # Get admin user who will take ownership
            admin_user = User.objects.filter(is_superuser=True).first()
            
            if not admin_user:
                messages.error(request, "No admin user found to transfer content to")
                return redirect('user_list')
            
            # Get all models that have foreign key to User
            user_related_models = []
            for model in apps.get_models():
                if any(isinstance(field, models.ForeignKey) and field.related_model == User 
                      for field in model._meta.fields):
                    user_related_models.append(model)
            
            # Transfer ownership of content to admin
            for model in user_related_models:
                # Get all user-related fields for this model
                user_fields = [
                    field.name for field in model._meta.fields
                    if isinstance(field, models.ForeignKey) 
                    and field.related_model == User
                ]
                
                # Update each field
                for field in user_fields:
                    filter_kwargs = {field: user}
                    update_kwargs = {field: admin_user}
                    model.objects.filter(**filter_kwargs).update(**update_kwargs)
                    
                    # Log the transfer
                    LogEntry.objects.create(
                        user_id=request.user.id,
                        content_type_id=ContentType.objects.get_for_model(model).id,
                        action_flag=DELETION,
                        change_message=f"Transferred {model.__name__} objects from {user.username} to admin"
                    )
            
            # Delete the user
            username = user.username
            user.delete()
            
            messages.success(
                request, 
                f'User {username} deleted successfully. All content transferred to admin.'
            )
            return redirect('user_list')
            
        except Exception as e:
            messages.error(request, f"Error during user deletion: {str(e)}")
            return redirect('user_list')
    
    # Count user's content
    content_summary = {}
    for model in apps.get_models():
        if hasattr(model, 'created_by'):
            count = model.objects.filter(created_by=user).count()
            if count > 0:
                content_summary[model.__name__] = count
    
    return render(request, 'registration/auth/delete_user.html', {
        'user_obj': user,
        'content_summary': content_summary
    })