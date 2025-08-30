from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    company_name = models.CharField(max_length=128)
    vacation_days = models.IntegerField()  

    def serialize(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            "vacation_days": self.vacation_days,
            }  

class Team(models.Model):
    team_name = models.CharField(max_length=64)
    team_company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="teams")

    def serialize(self):
        return {
            "id": self.id,
            "team_name": self.team_name,
            "team_company": self.team_company.company_name,
            }  

class Employee(models.Model):
    ROLES = {'admin': 'Admin', 'manager': 'Manager', 'employee': 'Employee'}
    employee = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_firstname = models.CharField(max_length=128)
    employee_lastname = models.CharField(max_length=128)
    employee_team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, related_name="team_members")
    employee_role = models.CharField(choices=ROLES)
    employement_date = models.DateField()
    
    def __str__(self):
        return self.employee.username
    
    def serialize(self):
        return {
            "id": self.id,
            "employee": self.employee,
            "employee_firstname": self.employee_firstname,
            "employee_lastname": self.employee_lastname,
            "employee_team": self.employee_team,
            "employee_role": self.employee_role,
            "employement_date": self.employement_date,
            }  
