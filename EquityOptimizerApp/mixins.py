from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import models


class CreatedAtMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True


class UpdatedAtMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class StaffUserRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(self.request.get_full_path())


class ObjectOwnershipRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.core.exceptions import PermissionDenied
        from django.contrib import messages

        messages.error(self.request, "You do not have permission to access this resource.")
        raise PermissionDenied("You do not have permission to access this resource.")
