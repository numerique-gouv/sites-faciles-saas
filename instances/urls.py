from django.urls import include, path

from instances import views

app_name = "instances"

urlpatterns = [
    path(
        "emailconfig/",
        include(
            [
                path(
                    "create/",
                    views.EmailConfigCreateView.as_view(),
                    name="emailconfig_create",
                ),
                path(
                    "<int:pk>/",
                    views.EmailConfigDetailView.as_view(),
                    name="emailconfig_detail",
                ),
                path(
                    "<int:pk>/update/",
                    views.EmailConfigUpdateView.as_view(),
                    name="emailconfig_update",
                ),
                path(
                    "<int:pk>/delete/",
                    views.EmailConfigDeleteView.as_view(),
                    name="emailconfig_delete",
                ),
                path("", views.EmailConfigListView.as_view(), name="emailconfig_list"),
            ]
        ),
    ),
    path(
        "scalingo_account/",
        include(
            [
                path(
                    "create/",
                    views.ScalingoAccountCreateView.as_view(),
                    name="scalingo_account_create",
                ),
                path(
                    "<int:pk>/",
                    views.ScalingoAccountDetailView.as_view(),
                    name="scalingo_account_detail",
                ),
                path(
                    "<int:pk>/update/",
                    views.ScalingoAccountUpdateView.as_view(),
                    name="scalingo_account_update",
                ),
                path(
                    "<int:pk>/delete/",
                    views.ScalingoAccountDeleteView.as_view(),
                    name="scalingo_account_delete",
                ),
                path(
                    "",
                    views.ScalingoAccountListView.as_view(),
                    name="scalingo_account_list",
                ),
            ]
        ),
    ),
    path(
        "storageconfig//",
        include(
            [
                path(
                    "create/",
                    views.StorageConfigCreateView.as_view(),
                    name="storageconfig_create",
                ),
                path(
                    "<int:pk>/",
                    views.StorageConfigDetailView.as_view(),
                    name="storageconfig_detail",
                ),
                path(
                    "<int:pk>/update/",
                    views.StorageConfigUpdateView.as_view(),
                    name="storageconfig_update",
                ),
                path(
                    "<int:pk>/delete/",
                    views.StorageConfigDeleteView.as_view(),
                    name="storageconfig_delete",
                ),
                path(
                    "",
                    views.StorageConfigListView.as_view(),
                    name="storageconfig_list",
                ),
            ]
        ),
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
