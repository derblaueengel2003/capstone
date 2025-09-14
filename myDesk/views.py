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


def index(request):
    return render(request, "myDesk/index.html")

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
    else:
        form = RequestForm(user=request.user)

    return render(request, "myDesk/request.html", {"form": form})

@login_required
def get_requests(request):
    vacation_requests = Request.objects.filter(request_user=request.user.profile.id).order_by("start_date", "end_date").values("start_date", "end_date", "approved", "request_user", "id")
    data = list(vacation_requests)
    return JsonResponse(data, safe=False)


@csrf_exempt
def edit_request(request, request_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            start_date = data.get("start_date")
            end_date = data.get("end_date")

            if not start_date or not end_date:
                return JsonResponse({"success": False, "errors": "Both dates are required."}, status=400)

            # parsing stringhe ISO "yyyy-mm-dd" in oggetti date
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

            today = datetime.date.today()
            if start_date < today:
                return JsonResponse({"success": False, "errors": "Start date cannot be in the past."}, status=400)
            if end_date < start_date:
                return JsonResponse({"success": False, "errors": "End date must be after start date."}, status=400)

            # prendo la richiesta da modificare
            try:
                vacation_request = Request.objects.get(pk=request_id, request_user=request.user.profile)
            except Request.DoesNotExist:
                return JsonResponse({"success": False, "errors": "Request not found."}, status=404)

            # controllo sovrapposizioni (escludendo la richiesta stessa)
            overlap = Request.objects.filter(
                request_user=request.user.profile,
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exclude(pk=vacation_request.pk)

            if overlap.exists():
                return JsonResponse({"success": False, "errors": "Dates overlap with an existing request."}, status=400)

            # aggiorno i campi
            vacation_request.start_date = start_date
            vacation_request.end_date = end_date
            vacation_request.approved = False  # reset approvazione dopo edit
            vacation_request.save()

            return JsonResponse({
                "success": True,
                "request": {
                    "id": vacation_request.id,
                    "start_date": str(vacation_request.start_date),
                    "end_date": str(vacation_request.end_date),
                    "approved": vacation_request.approved,
                }
            })

        except ValidationError as e:
            return JsonResponse({"success": False, "errors": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "errors": str(e)}, status=500)

    return JsonResponse({"success": False, "errors": "Invalid method."}, status=405)


@csrf_exempt
def delete_request(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            request_id = data.get("request_id")

            req = Request.objects.get(pk=request_id, request_user=request.user.profile)
            req.delete()

            return JsonResponse({"success": True})
        except Request.DoesNotExist:
            return JsonResponse({"success": False, "errors": "Request not found."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "errors": str(e)}, status=500)

    return JsonResponse({"success": False, "errors": "Invalid method."}, status=405)

