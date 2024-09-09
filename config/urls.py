"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic import RedirectView
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=staticfiles_storage.url("dsfr/dist/favicon/favicon.ico")
        ),
    ),
    path("", include("core.urls")),
    path("admin/", admin.site.urls),
]

# Only add this on a dev machine, outside of tests
if not settings.TESTING and settings.DEBUG and "localhost" in settings.HOST_URL:
    urlpatterns += debug_toolbar_urls()
