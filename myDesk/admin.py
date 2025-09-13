from django.contrib import admin

from .models import Team, Profile, Company, Request

# Register your models here.
admin.site.register(Team)
admin.site.register(Profile)
admin.site.register(Company)
admin.site.register(Request)