from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("edit-user", views.edit_user, name="edit_user"),
    path("admin-dashboard", views.admin_dashboard, name="admin_dashboard"),
    path("add-company", views.company, name="add_company"),
    path("edit-company", views.edit_company, name="edit_company"),
    path("delete-company", views.delete_company, name="delete_company"),
    path("add-team", views.team, name="add_team"),
    path("edit-team", views.edit_team, name="edit_team"),
    path("delete-team", views.delete_team, name="delete_team"),
    path("edit-employee", views.edit_employee, name="edit_employee"),
    path("delete-employee", views.toggle_employee_status, name="toggle_employee_status"),
    path("requests", views.vacation_request, name="vacation_requests"),
    path("get-requests", views.get_requests, name="get_vacation_requests"),
    path("add-request", views.vacation_request, name="add_request"),
    path("edit-request", views.edit_request, name="edit_request"),
    path("delete-request", views.delete_request, name="delete_request"),
]