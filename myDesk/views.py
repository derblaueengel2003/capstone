from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.contrib import messages
from django.core.exceptions import ValidationError
import json
from adminDashboard.models import Profile
from .models import Request


def get_vacation_usage(profile, year=None):
    # This helper function is used to calculate how many vacation days the user has left
    # approved vacations are subtracted from the annual amount.
    if year is None:
        year = datetime.date.today().year

    approved_requests = profile.vacation_requests.filter(
        processed=True,
        approved=True,
        start_date__year=year,
    )

    days_used = 0
    for vacation_request in approved_requests:
        days_difference = vacation_request.end_date - vacation_request.start_date
        days_used += days_difference.days + 1
    days_remaining = profile.vacation_days - days_used
    return year, days_used, days_remaining


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
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise ValidationError("You already have a vacation request overlapping these dates.")

        return cleaned_data


class ManagerDecisionForm(forms.Form):
    manager_message = forms.CharField(
        label="Message for the employee",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        required=False,
    )

@login_required
def index(request):
    profile = request.user.profile
    vacation_requests = (
        Request.objects.filter(request_user=profile)
        .select_related("request_user__user")
        .order_by("start_date", "end_date")
    )

    manager_pending_requests = None
    user_summary = None
    admin_profiles_to_process = None

    if profile.role == "Manager":
        pending_qs = Request.objects.none()
        if profile.team:
            pending_qs = Request.objects.filter(
                request_user__team=profile.team,
                processed=False,
            )
        manager_pending_requests = pending_qs.count()
    else:
        summary_year, days_used, days_remaining = get_vacation_usage(profile)
        user_summary = {
            "total": vacation_requests.count(),
            "approved": vacation_requests.filter(processed=True, approved=True).count(),
            "denied": vacation_requests.filter(processed=True, approved=False).count(),
            "pending": vacation_requests.filter(processed=False).count(),
            "vacation_days": profile.vacation_days,
            "year": summary_year,
            "days_used": days_used,
            "days_remaining": days_remaining,
        }

    if request.user.is_staff:
        admin_profiles_to_process = 0
        for profile_record in Profile.objects.all():
            if profile_record.team is None:
                needs_team = True
            else:
                needs_team = False

            if profile_record.employment_date is None:
                needs_employment_date = True
            else:
                needs_employment_date = False

            if profile_record.vacation_days <= 0:
                needs_vacation_days = True
            else:
                needs_vacation_days = False
            if needs_team or needs_employment_date or needs_vacation_days:
                admin_profiles_to_process += 1

    return render(request, "myDesk/index.html", {
        "vacation_requests": vacation_requests,
        "vacation_request_form": RequestForm(user=request.user),
        "manager_pending_requests": manager_pending_requests,
        "user_summary": user_summary,
        "admin_profiles_to_process": admin_profiles_to_process,
        "team": profile.team,
    })

@login_required
@csrf_exempt
def vacation_request(request):
    usage_year, used_days, remaining_days = get_vacation_usage(request.user.profile)

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
                request_user=request.user.profile
            ).select_related("request_user__user").order_by("start_date", "end_date")

            return render(request, "myDesk/request.html", {
                "vacation_requests": vacation_requests,
                "vacation_request_form": form,
                "vacation_days_remaining": remaining_days,
                "vacation_days_used": used_days,
                "vacation_days_total": request.user.profile.vacation_days,
                "vacation_year": usage_year,
            })

    # GET
    vacation_requests = Request.objects.filter(
        request_user=request.user.profile
    ).select_related("request_user__user").order_by("start_date", "end_date")

    return render(request, "myDesk/request.html", {
        "vacation_requests": vacation_requests,
        "vacation_request_form": RequestForm(user=request.user),
        "vacation_days_remaining": remaining_days,
        "vacation_days_used": used_days,
        "vacation_days_total": request.user.profile.vacation_days,
        "vacation_year": usage_year,
    })


@login_required
@csrf_exempt
def edit_request(request, request_id):
    vacation_request = Request.objects.get(pk=request_id, request_user=request.user.profile)

    if request.method == "POST":
        form = RequestForm(request.POST, instance=vacation_request, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Vacation request updated successfully.")
            return redirect("vacation_requests")  
        else:
            messages.error(request, "Please correct the errors below.")
            usage_year, used_days, remaining_days = get_vacation_usage(request.user.profile)
            return render(request, "myDesk/request.html", {
                "vacation_requests": Request.objects.filter(
                    request_user=request.user.profile
                )
                .select_related("request_user__user")
                .order_by("start_date", "end_date"),
                "vacation_request_form": form,
                "vacation_days_remaining": remaining_days,
                "vacation_days_used": used_days,
                "vacation_days_total": request.user.profile.vacation_days,
                "vacation_year": usage_year,
            })

    # GET
    form = RequestForm(instance=vacation_request, user=request.user)
    return render(request, "myDesk/edit-request.html", {
        "form": form,
        "vacation_request": vacation_request
    })
    
@login_required
@csrf_exempt
def delete_request(request, request_id):
    vacation_request = Request.objects.get(pk=request_id, request_user=request.user.profile)

    if request.method == "POST":
        vacation_request.delete()
        messages.success(request, "Vacation request deleted successfully.")
        return redirect("vacation_requests")

    # GET: chiedo conferma
    return render(request, "myDesk/delete-request.html", {
        "vacation_request": vacation_request
    })

@login_required
@csrf_exempt
def manage_request(request):
    profile = request.user.profile

    if profile.role != "Manager":
        return HttpResponseForbidden("Only managers can view team vacation requests.")

    team = profile.team

    if not team:
        vacation_requests = Request.objects.none()
    else:
        team_requests_qs = (
            Request.objects.filter(request_user__team=team)
            .select_related("request_user__user")
            .order_by("start_date", "end_date")
        )
        profile_ids = list(
            team_requests_qs.values_list("request_user_id", flat=True).distinct()
        )
        member_profiles = Profile.objects.filter(id__in=profile_ids)

        usage_lookup = {}
        for member in member_profiles:
            year, used_days, remaining_days = get_vacation_usage(member)
            usage_lookup[member.id] = {
                "year": year,
                "used": used_days,
                "remaining": remaining_days,
                "total": member.vacation_days,
            }

        vacation_requests = list(team_requests_qs)
        for vacation in vacation_requests:
            usage = usage_lookup.get(vacation.request_user_id)
            if usage:
                vacation.usage_year = usage["year"]
                vacation.usage_days_used = usage["used"]
                vacation.usage_days_remaining = usage["remaining"]
                vacation.usage_days_total = usage["total"]
    return render(
        request,
        "myDesk/manage-requests.html",
        {
            "team": team,
            "vacation_requests": vacation_requests,
        },
    )


@login_required
@csrf_exempt
def approve_request(request, request_id):
    profile = request.user.profile

    if profile.role != "Manager":
        return HttpResponseForbidden("Only managers can approve vacation requests.")

    vacation_request = Request.objects.select_related(
        "request_user__team",
        "request_user__user"
    ).filter(pk=request_id).first()
    if not vacation_request:
        return HttpResponseForbidden("The vacation request you are looking for does not exist.")

    if vacation_request.request_user.team != profile.team:
        return HttpResponseForbidden("You can only approve requests from your team.")

    if request.method == "POST":
        form = ManagerDecisionForm(request.POST)
        if form.is_valid():
            vacation_request.approved = True
            vacation_request.processed = True
            vacation_request.manager_message = form.cleaned_data["manager_message"]
            vacation_request.save()
            messages.success(request, "Vacation request approved.")
            return redirect("manage_requests")
    else:
        form = ManagerDecisionForm(
            initial={"manager_message": vacation_request.manager_message}
        )

    return render(
        request,
        "myDesk/approve-request.html",
        {
            "vacation_request": vacation_request,
            "form": form,
        },
    )


@login_required
@csrf_exempt
def deny_request(request, request_id):
    profile = request.user.profile

    if profile.role != "Manager":
        return HttpResponseForbidden("Only managers can deny vacation requests.")

    vacation_request = Request.objects.select_related(
        "request_user__team",
        "request_user__user"
    ).filter(pk=request_id).first()
    if not vacation_request:
        return HttpResponseForbidden("The vacation request you are looking for does not exist.")

    if vacation_request.request_user.team != profile.team:
        return HttpResponseForbidden("You can only deny requests from your team.")

    if request.method == "POST":
        form = ManagerDecisionForm(request.POST)
        if form.is_valid():
            vacation_request.approved = False
            vacation_request.processed = True
            vacation_request.manager_message = form.cleaned_data["manager_message"]
            vacation_request.save()
            messages.success(request, "Vacation request denied.")
            return redirect("manage_requests")
    else:
        form = ManagerDecisionForm(
            initial={"manager_message": vacation_request.manager_message}
        )

    return render(
        request,
        "myDesk/deny-request.html",
        {
            "vacation_request": vacation_request,
            "form": form,
        },
    )
