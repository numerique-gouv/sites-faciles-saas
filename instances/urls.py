from django.urls import path

from instances import views

app_name = "instances"

urlpatterns = [
    path("", views.InstanceListView.as_view(), name="list"),
    path("create/", views.InstanceCreateView.as_view(), name="create"),
    path("<int:pk>/", views.InstanceUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.InstanceDeleteView.as_view(), name="delete"),
]
