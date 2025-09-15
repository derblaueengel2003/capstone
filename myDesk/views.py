from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Request
from django import forms
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.contrib import messages
from django.core.exceptions import ValidationError
import json


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['start_date', 'end_date']
        widgets = {
            "start_date": forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}),
            "end_date": forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # I need to get the current user from the view
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if not start_date or not end_date:
            raise ValidationError("Start date and end date are mandatory.")

        today = datetime.date.today()
        if start_date < today:
            raise ValidationError("Start date cannot be in the past.")
        if end_date < start_date:
            raise ValidationError("Start date cannot be after end date.")

        # Check if there are overlapping requests
        if self.user:
            overlapping = Request.objects.filter(
                request_user=self.user.profile,
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            if self.instance.pk:  # editing of an existing request
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise ValidationError("You already have a vacation request overlapping these dates.")

        return cleaned_data

@login_required
def index(request):
    vacation_requests = Request.objects.filter(request_user=request.user.profile.id).order_by("start_date", "end_date").values()
    return render(request, "myDesk/index.html", {
        "vacation_requests": vacation_requests,
        "vacation_request_form": RequestForm()
    })

@login_required
@csrf_exempt
def vacation_request(request):
    if request.method == "POST":
        form = RequestForm(request.POST, user=request.user)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.request_user = request.user.profile
            new_request.approved = False
            new_request.save()
            messages.success(request, 'Your request was sent')
            return redirect("vacation_requests")  
        else:
            messages.error(request, 'Please correct the errors below.')
            vacation_requests = Request.objects.filter(
                request_user=request.user.profile.id
            ).order_by("start_date", "end_date").values()

            return render(request, "myDesk/request.html", {
                "vacation_requests": vacation_requests,
                "vacation_request_form": form  # ritorno il form con errori
            })

    # GET
    vacation_requests = Request.objects.filter(
        request_user=request.user.profile.id
    ).order_by("start_date", "end_date").values()

    return render(request, "myDesk/request.html", {
        "vacation_requests": vacation_requests,
        "vacation_request_form": RequestForm(user=request.user)
    })



@csrf_exempt
def edit_request(request, request_id):
    pass


@csrf_exempt
def delete_request(request):
   pass

