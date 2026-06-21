# authentication/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
# Delete models


# Define the function first
def get_admin_user():
    User = get_user_model()
    admin = User.objects.filter(is_superuser=True).first()
    if admin:
        return admin.id
    return None

# Then use it in the BaseModel
class BaseModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_admin_user),  # Now this will work
        related_name="%(class)s_created",null=True
    )
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        abstract = True