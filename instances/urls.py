from django.urls import path

from instances import views

urlpatterns = [
    path("", views.index, name="index"),
]
