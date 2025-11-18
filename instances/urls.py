from django.conf import settings
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
        "emailconfig/<int:pk>/delete/",
        views.EmailConfigDeleteView.as_view(),
        name="emailconfig_delete",
    ),
    path(
        "storageconfig/",
        views.StorageConfigListView.as_view(),
        name="storageconfig_list",
    ),
    path(
        "storageconfig/create/",
        views.StorageConfigCreateView.as_view(),
        name="storageconfig_create",
    ),
    path(
        "storageconfig/<int:pk>/",
        views.StorageConfigDetailView.as_view(),
        name="storageconfig_detail",
    ),
    path(
        "storageconfig/<int:pk>/update/",
        views.StorageConfigUpdateView.as_view(),
        name="storageconfig_update",
    ),
    path(
        "storageconfig/<int:pk>/delete/",
        views.StorageConfigDeleteView.as_view(),
        name="storageconfig_delete",
    ),
    path("", views.InstanceListView.as_view(), name="list"),
]

if settings.INSTANCES_ALLOW_CREATE:
    urlpatterns += [
        path("create/", views.InstanceCreateView.as_view(), name="create"),
    ]

urlpatterns += [
    path(
        "mass_deploy/",
        views.InstanceMassDeployFormView.as_view(),
        name="mass_deploy_list",
    ),
    path("<str:slug>/", views.InstanceDetailView.as_view(), name="detail"),
    path("<str:slug>/update/", views.InstanceUpdateView.as_view(), name="update"),
    path(
        "<str:slug>/action/",
        views.InstanceActionView.as_view(),
        name="action",
    ),
]

if settings.INSTANCES_ALLOW_DELETE:
    urlpatterns += [
        path("<str:slug>/delete/", views.InstanceDeleteView.as_view(), name="delete"),
    ]
