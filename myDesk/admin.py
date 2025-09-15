from django.contrib import admin
from adminDashboard.models import Team, Company, Profile
from .models import Request


# Register your models here.
admin.site.register(Team)
admin.site.register(Profile)
admin.site.register(Company)
admin.site.register(Request)