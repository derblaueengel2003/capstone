from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("edit-profile", views.edit_profile, name="edit_profile"),
    path("admin-dashboard", views.admin_dashboard, name="admin_dashboard"),
    path("add-company", views.company, name="add_company"),
    path("edit-company", views.edit_company, name="edit_company"),
    path("delete-company", views.delete_company, name="delete_company"),
    path("add-team", views.team, name="add_team"),
    path("edit-team", views.edit_team, name="edit_team"),
    path("delete-team", views.delete_team, name="delete_team"),
    path("add-employee", views.employee, name="add_employee"),
    path("edit-employee", views.edit_employee, name="edit_employee"),
    path("delete-employee", views.delete_employee, name="delete_employee"),
]