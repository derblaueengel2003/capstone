from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Company, Team, Profile
from django import forms
from django.views.decorators.csrf import csrf_exempt
import json

# Forms with css class associated
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['company_name', 'id']
        widgets = {
            "company_name": forms.TextInput(attrs={'class': 'form-control'}),
        }

class TeamForm(forms.ModelForm): 
    class Meta:
        model = Team
        fields = ["team_name", "id"]
        widgets = {
            "team_name": forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["user", "team", "role", "employment_date", "vacation_days", "id"]


@login_required
def admin_dashboard(request):
    companies = Company.objects.all().order_by('company_name').values()
    teams = Team.objects.all().order_by('team_name').values()
    employees = Profile.objects.all().order_by('team')


    #If the user has is_staff permission then he can access the admin
    #dashboard. Otherwise he will be redirect to the homepage
    if getattr(request.user, "is_staff"):
        return render(request, "adminDashboard/admin-dashboard.html", {
            "companies": companies,
            "teams": teams,
            "employees": employees,
            "company_form": CompanyForm(),
            "team_form": TeamForm(),
            "profile_form": ProfileForm(),
        })
    else:
        return HttpResponseRedirect(reverse("index"))
    
def company(request):

    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            new_company = Company(
                company_name=form.cleaned_data["company_name"], 
                )
            new_company.save()

    return HttpResponseRedirect(reverse("admin_dashboard"))

@csrf_exempt
def edit_company(request):
    data = json.loads(request.body)
    company = Company.objects.get(pk=data['company_id'])
    company.company_name = data['company_name']
    company.save()
    return JsonResponse(company.serialize())

@csrf_exempt
def delete_company(request):
    data = json.loads(request.body)
    company_to_delete = Company.objects.get(pk=data['company_id'])
    company_to_delete.delete()
    return JsonResponse(company_to_delete.serialize())

def team(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            new_team = Team(
                team_name=form.cleaned_data["team_name"],
                )
            new_team.save()

    return HttpResponseRedirect(reverse("admin_dashboard"))

@csrf_exempt
def edit_team(request):
    data = json.loads(request.body)
    team = Team.objects.get(pk=data['team_id'])

    team.team_name = data['team_name']
    team.save()
    return JsonResponse(team.serialize())

@csrf_exempt
def delete_team(request):
    data = json.loads(request.body)
    team_to_delete = Team.objects.get(pk=data['team_id'])
    team_to_delete.delete()
    return JsonResponse(team_to_delete.serialize())

@csrf_exempt
def edit_employee(request):
    data = json.loads(request.body)
    print(request.body)
    employee = Profile.objects.get(pk=data['employee_id'])

# check if the form gives me a team name and this name is not "remove"
    if data['team'] and data['team'] != 'remove':
        employee.team = Team.objects.get(pk=data['team'])
    elif data['team'] == 'remove':
        employee.team = None
    employee.role = data["role"]
    if data['employment_date']:
        employee.employment_date = data["employment_date"]
    employee.vacation_days = data["vacation_days"]
    employee.save()
    return JsonResponse(employee.serialize())

@csrf_exempt
def toggle_employee_status(request):
    data = json.loads(request.body)
    employee_to_delete = Profile.objects.get(pk=data['employee_id'])
    employee_to_delete.user.is_active = not employee_to_delete.user.is_active
    employee_to_delete.user.save()
    return JsonResponse(employee_to_delete.serialize())
