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

class Profile(models.Model):
    ROLES = {'Admin': 'Admin', 'Manager': 'Manager', 'Employee': 'Employee'}
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name="team_members", null=True, blank=True)
    role = models.CharField(choices=ROLES, default='Employee', max_length=16)
    employment_date = models.DateField(null=True, blank=True)
    vacation_days = models.IntegerField(default=20)  
    
    def __str__(self):
        return self.user.username
    
    def serialize(self):
        team = {}
        if self.team:
            team['id'] = self.team.id
            team['team_name'] = self.team.team_name
        return {
            "id": self.id,
            "team": team,
            "role": self.role,
            "employment_date": self.employment_date,
            "vacation_days": self.vacation_days,
            }  

# if User is created or updated then the associate Profile should be
# created or updated too.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
