from django.contrib import admin

from .models import Team, Profile, Company

# Register your models here.
admin.site.register(Team)
admin.site.register(Profile)
admin.site.register(Company)