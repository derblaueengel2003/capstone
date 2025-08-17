from django.db import models

class Team(models.Model):
    team_name = models.CharField(max_length=64)
