from django.urls import path

from contacts import views

app_name = "contacts"

urlpatterns = [
    path("", views.ContactListView.as_view(), name="list"),
    path("create/", views.ContactCreateView.as_view(), name="create"),
    path("<int:pk>/", views.ContactUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.ContactDeleteView.as_view(), name="delete"),
]
