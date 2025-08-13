"""
Model mixins for enhanced functionality.
These add common features to your models without repeating code.
"""
from django.db import models
from django.utils import timezone
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE


class TimestampMixin(models.Model):
    """
    Mixin to add created_at and updated_at timestamps to models.
    Like having a digital signature on when things were created/modified.
    """
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(SafeDeleteModel):
    """
    Mixin to add soft delete functionality to models.
    Instead of permanently deleting, just marks as deleted.
    """
    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        abstract = True


class AuditMixin(models.Model):
    """
    Mixin to add audit fields for tracking who made changes.
    Useful for compliance and debugging.
    """
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text="User who created this record"
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text="User who last updated this record"
    )

    class Meta:
        abstract = True


class BaseModel(TimestampMixin, SoftDeleteMixin, AuditMixin):
    """
    Base model that combines all our mixins.
    All your models can inherit from this for consistent functionality.
    """
    class Meta:
        abstract = True