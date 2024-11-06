from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse


def check_admin(user):
    return user.is_superuser


@user_passes_test(check_admin)
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")  # type:ignore
