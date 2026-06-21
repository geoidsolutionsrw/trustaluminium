from django.db import models

# ─────────────────────────────────────────────────────────────────────────────
# ADD THIS to dash/models.py  (create the file if it doesn't exist)
# ─────────────────────────────────────────────────────────────────────────────

from django.db import models
from django.contrib.auth.models import User


class QuotationNotification(models.Model):
    """Stores popup notifications for new public quotation requests."""

    quotation_id   = models.IntegerField()
    customer_name  = models.CharField(max_length=255)
    phone_number   = models.CharField(max_length=50, blank=True)
    product_count  = models.IntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)
    is_read        = models.BooleanField(default=False)
    read_by        = models.ManyToManyField(User, blank=True, related_name='read_notifications')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification: Quotation #{self.quotation_id} — {self.customer_name}"
    