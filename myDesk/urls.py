from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("requests", views.vacation_request, name="vacation_requests"),
    path("add-request", views.vacation_request, name="add_request"),
    path("edit-request/<int:request_id>/", views.edit_request, name="edit_request"),
    path("delete-request", views.delete_request, name="delete_request"),
]