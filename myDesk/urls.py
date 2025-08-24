from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("admin-dashboard", views.admin_dashboard, name="admin_dashboard"),
    path("add-company", views.company, name="add_company"),
    path("edit-company", views.edit_company, name="edit_company"),
    path("delete-company", views.delete_company, name="delete_company"),
]