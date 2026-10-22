from contextlib import contextmanager
from importlib import reload

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import clear_url_caches
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice


def create_user(username="user", is_staff=False, **kwargs):
    return get_user_model().objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="password",
        is_staff=is_staff,
        **kwargs,
    )


def login_with_otp(client, user):
    """
    Logs the user in and marks the session as verified by a TOTP device
    """
    device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    client.force_login(user)
    session = client.session
    session[DEVICE_ID_SESSION_KEY] = device.persistent_id
    session.save()


@contextmanager
def reloaded_urls(**flags):
    """
    Some URLs are only declared when a setting is enabled at import time
    (e.g. INSTANCES_ALLOW_CREATE), so the URLconf has to be reloaded
    """
    import config.urls
    import instances.urls

    def reload_urls():
        reload(instances.urls)
        reload(config.urls)
        clear_url_caches()

    try:
        with override_settings(**flags):
            reload_urls()
            yield
    finally:
        reload_urls()
