from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import gettext as _
from django.http import Http404
from django.contrib.auth.models import User

class ProductChangePermissionRequiredMixin(PermissionRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object().created_by 
        if user != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class IsStaffPermissionRequiredMixin(PermissionRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        return self.handle_no_permission()

class OwnerExistsMixin():

    def set_owner(self, pk):
        if User.objects.filter(pk=pk).exists():
                self.owner = User.objects.get(pk=pk)
        else:
            raise Http404(
                _(f"Owner with id {pk} not found.")
            )
