from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Company, Team, Profile
from django.contrib.auth.models import User
from django import forms
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.forms import ModelChoiceField, CharField
from django.contrib import messages
from datetime import datetime



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
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["user", "team", "role", "employment_date", "vacation_days", "id"]

def index(request):
    return render(request, "myDesk/index.html")

def edit_user(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        # profile_form = ProfileForm(request.POST, instance=request.user.profile)
        # if user_form.is_valid() and profile_form.is_valid():
        if user_form.is_valid():
            user_form.save()
            # profile_form.save()
            messages.success(request, ('Your profile was successfully updated!'))
            
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        # profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'myDesk/profile.html', {
        'user_form': user_form,
        # 'profile_form': profile_form
    })

@login_required()
def admin_dashboard(request):
    companies = Company.objects.all().order_by('company_name').values()
    teams = Team.objects.all().order_by('team_name').values()
    employees = Profile.objects.all().order_by('role')


    #If the user has is_staff permission then he can access the admin
    #dashboard. Otherwise he will be redirect to the homepage
    if getattr(request.user, "is_staff"):
        return render(request, "myDesk/admin-dashboard.html", {
            "companies": companies,
            "teams": teams,
            "employees": employees,
            "company_form": CompanyForm(),
            "team_form": TeamForm(),
            "profile_form": ProfileForm(),
            "user_form": UserForm(),
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

def employee(request):
    if request.method == "POST":
        print(request)
        form = ProfileForm(request.POST)
        if form.is_valid():
            new_employee = Profile(
                team=form.cleaned_data["team"],
                role=form.cleaned_data["role"],
                employment_date=datetime.strptime(form.cleaned_data["employment_date"], "%Y-%m-%d"),
                vacation_days=form.cleaned_data["vacation_days"],  
                )
            new_employee.save()

    return HttpResponseRedirect(reverse("admin_dashboard"))

@csrf_exempt
def edit_employee(request):
    data = json.loads(request.body)
    print(request.body)
    employee = Profile.objects.get(pk=data['employee_id'])

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


#da rivedere, meglio disattivare che cancellare
@csrf_exempt
def toggle_employee_status(request):
    data = json.loads(request.body)
    employee_to_delete = Profile.objects.get(pk=data['employee_id'])
    employee_to_delete.user.is_active = not employee_to_delete.user.is_active
    employee_to_delete.user.save()
    return JsonResponse(employee_to_delete.serialize())



