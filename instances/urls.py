from django.urls import path

from instances import views

app_name = "instances"

urlpatterns = [
    path("emailconfig/", views.EmailConfigListView.as_view(), name="emailconfig_list"),
    path(
        "emailconfig/create/",
        views.EmailConfigCreateView.as_view(),
        name="emailconfig_create",
    ),
    path(
        "emailconfig/<int:pk>/",
        views.EmailConfigDetailView.as_view(),
        name="emailconfig_detail",
    ),
    path(
        "emailconfig/<int:pk>/update/",
        views.EmailConfigUpdateView.as_view(),
        name="emailconfig_update",
    ),
    path(
        "emailconfig/<str:slug>/delete/",
        views.InstanceDeleteView.as_view(),
        name="emailconfig_delete",
    ),
    path("", views.InstanceListView.as_view(), name="list"),
    path("create/", views.InstanceCreateView.as_view(), name="create"),
    path("<str:slug>/", views.InstanceDetailView.as_view(), name="detail"),
    path("<str:slug>/update/", views.InstanceUpdateView.as_view(), name="update"),
    path(
        "<str:slug>/action/",
        views.InstanceActionView.as_view(),
        name="action",
    ),
    path("<str:slug>/delete/", views.InstanceDeleteView.as_view(), name="delete"),
]
