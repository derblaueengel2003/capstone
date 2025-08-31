from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Company(models.Model):
    company_name = models.CharField(max_length=128)

    def serialize(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            }  

class Team(models.Model):
    team_name = models.CharField(max_length=64)
    
    def __str__(self):
        return self.team_name
    
    def serialize(self):
        return {
            "id": self.id,
            "team_name": self.team_name,
            }  

class Request(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

class Profile(models.Model):
    ROLES = {'Admin': 'Admin', 'Manager': 'Manager', 'Employee': 'Employee'}
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, related_name="team_members", null=True, blank=True)
    role = models.CharField(choices=ROLES, null=True, blank=True)
    employement_date = models.DateField(null=True, blank=True)
    vacation_days = models.IntegerField(null=True, blank=True)  
    vacation_request = models.ForeignKey(Request, on_delete=models.DO_NOTHING, related_name='vacation_requests',null=True, blank=True)
    
    def __str__(self):
        return self.user.username
    
    def serialize(self):
        return {
            "id": self.id,
            "user": self.user,
            "team": self.team,
            "role": self.role,
            "employement_date": self.employement_date,
            "vacation_days": self.vacation_days,
            "vacation_request": self.vacation_request,
            }  

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()