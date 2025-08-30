from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Company, Team, Employee
from django import forms
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.forms import ModelChoiceField



class CompanyForm(forms.Form):
    company_name = forms.CharField(max_length=128)
    vacation_days = forms.IntegerField()

class TeamForm(forms.ModelForm):
    
    class Meta:
        model = Team
        fields = ["team_name", "team_company", "id"]
    
    class MyModelChoiceField(ModelChoiceField):
        def label_from_instance(self, obj):
            print(obj)
            return obj.company_name
    
    team_company = MyModelChoiceField(queryset=Company.objects.all(), required=True, empty_label=None)

def index(request):
    return render(request, "myDesk/index.html", {})

@login_required()
def admin_dashboard(request):
    companies = Company.objects.all().order_by('company_name').values()
    teams = Team.objects.all().order_by('team_company')
    employees = Employee.objects.all().order_by('employee_lastname').values()

    #If the user has is_staff permission then he can access the admin
    #dashboard. Otherwise he will be redirect to the homepage
    if getattr(request.user, "is_staff"):
        return render(request, "myDesk/admin-dashboard.html", {
            "companies": companies,
            "teams": teams,
            "employees": employees,
            "company_form": CompanyForm(),
            "team_form": TeamForm()
        })
    else:
        return HttpResponseRedirect(reverse("index"))
    
def company(request):

    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            new_company = Company(
                company_name=form.cleaned_data["company_name"], 
                vacation_days=form.cleaned_data["vacation_days"],
                )
            new_company.save()

    return HttpResponseRedirect(reverse("admin_dashboard"))

@csrf_exempt
def edit_company(request):
    data = json.loads(request.body)
    company = Company.objects.get(pk=data['company_id'])
    company.company_name = data['company_name']
    company.vacation_days = data['vacation_days']
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
                team_company=form.cleaned_data["team_company"],
                )
            new_team.save()

    return HttpResponseRedirect(reverse("admin_dashboard"))

@csrf_exempt
def edit_team(request):
    data = json.loads(request.body)
    team = Team.objects.get(pk=data['team_id'])

    team.team_name = data['team_name']
    team.team_company = Company.objects.get(pk=data['team_company'])
    team.save()
    return JsonResponse(team.serialize())

@csrf_exempt
def delete_team(request):
    data = json.loads(request.body)
    team_to_delete = Team.objects.get(pk=data['team_id'])
    team_to_delete.delete()
    return JsonResponse(team_to_delete.serialize())


