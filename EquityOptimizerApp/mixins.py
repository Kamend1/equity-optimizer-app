from django.db import models
from django.utils import timezone


class CreatedAtMixin(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        abstract = True


class UpdatedAtMixin(models.Model):
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        abstract = True
