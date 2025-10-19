from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add-request", views.add_request, name="add_request"),
    path("edit-request", views.edit_request, name="edit_request"),
    path("delete-request", views.delete_request, name="delete_request"),
    path("update-request-status", views.update_request_status, name="update_request_status"),
]
