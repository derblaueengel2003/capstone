from django.db import models

class Company(models.Model):
    company_name = models.CharField(max_length=128)
    vacation_days = models.IntegerField()

class Team(models.Model):
    team_name = models.CharField(max_length=64)
    team_company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="teams")

class Employee(models.Model):
    ROLES = {'admin': 'Admin', 'manager': 'Manager', 'employee': 'Employee'}
    employee_name = models.CharField(max_length=128)
    employee_team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, related_name="team_members")
    employee_role = models.CharField(choices=ROLES)
    employement_date = models.DateField()

