from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView, TemplateView
from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=staticfiles_storage.url("dsfr/dist/favicon/favicon.ico")
        ),
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path(
        "account/logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path("contacts/", include("contacts.urls")),
    path("instances/", include("instances.urls")),
    path("admin/", admin.site.urls),
    path("", include(tf_urls)),
    path("", include("core.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# Only add this on a dev machine, outside of tests
if not settings.TESTING and settings.DEBUG and "localhost" in settings.HOST_URL:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
