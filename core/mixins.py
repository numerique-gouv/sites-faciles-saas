from django.contrib.auth.mixins import UserPassesTestMixin

from core.utils import check_staff_or_admin


class StaffOrAdminMixin(UserPassesTestMixin):
    def test_func(self):
        return check_staff_or_admin(self.request.user)  # type: ignore
