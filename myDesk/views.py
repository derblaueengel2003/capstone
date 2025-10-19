from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.core.exceptions import ValidationError
import json
from adminDashboard.models import Profile
from .models import Request


def get_vacation_usage(profile, year=None):
    if year is None:
        today = datetime.date.today()
        year = today.year

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
        fields = ["start_date", "end_date"]
        widgets = {
            "start_date": forms.TextInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.TextInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if not start_date or not end_date:
            raise ValidationError("Start date and end date are mandatory.")

        today = datetime.date.today()
        if start_date < today:
            raise ValidationError("Start date cannot be in the past.")

        if end_date < start_date:
            raise ValidationError("End date cannot be before start date.")

        if self.user:
            overlapping = Request.objects.filter(
                request_user=self.user.profile,
                start_date__lte=end_date,
                end_date__gte=start_date,
            )
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise ValidationError("You already have a vacation request for these dates.")

        return cleaned_data


@login_required
def index(request):
    profile = request.user.profile

    my_requests_qs = (
        Request.objects.filter(request_user=profile)
        .select_related("request_user__user")
        .order_by("start_date", "end_date")
    )
    my_requests = list(my_requests_qs)

    for vacation_request in my_requests:
        days_difference = vacation_request.end_date - vacation_request.start_date
        vacation_request.total_days = days_difference.days + 1
        if vacation_request.processed:
            if vacation_request.approved:
                vacation_request.status_label = "Approved"
            else:
                vacation_request.status_label = "Denied"
        else:
            vacation_request.status_label = "Pending"

    summary_year, days_used, days_remaining = get_vacation_usage(profile)

    user_summary = {
        "year": summary_year,
        "vacation_days": profile.vacation_days,
        "days_used": days_used,
        "days_remaining": days_remaining,
        "total": len(my_requests),
        "approved": 0,
        "denied": 0,
        "pending": 0,
    }

    for vacation_request in my_requests:
        if vacation_request.processed:
            if vacation_request.approved:
                user_summary["approved"] += 1
            else:
                user_summary["denied"] += 1
        else:
            user_summary["pending"] += 1

    manager_team_requests = []
    manager_pending_requests = 0
    manager_usage = {}

    if profile.role == "Manager" and profile.team:
        team_requests_qs = (
            Request.objects.filter(request_user__team=profile.team)
            .select_related("request_user__user")
            .order_by("start_date", "end_date")
        )
        manager_team_requests = list(team_requests_qs)

        member_profiles = []
        member_ids = []
        for team_request in manager_team_requests:
            if not team_request.processed:
                manager_pending_requests += 1

            member_id = team_request.request_user_id
            if member_id not in member_ids:
                member_ids.append(member_id)
                member_profiles.append(team_request.request_user)

        for member in member_profiles:
            year, used_days, remaining_days = get_vacation_usage(member)
            manager_usage[member.id] = {
                "year": year,
                "used": used_days,
                "remaining": remaining_days,
                "total": member.vacation_days,
            }

        for team_request in manager_team_requests:
            usage = manager_usage.get(team_request.request_user_id)
            if usage:
                team_request.usage_year = usage["year"]
                team_request.usage_used = usage["used"]
                team_request.usage_remaining = usage["remaining"]
                team_request.usage_total = usage["total"]
            else:
                team_request.usage_year = summary_year
                team_request.usage_used = 0
                team_request.usage_remaining = team_request.request_user.vacation_days
                team_request.usage_total = team_request.request_user.vacation_days

            days_difference = team_request.end_date - team_request.start_date
            team_request.total_days = days_difference.days + 1
            if team_request.processed:
                if team_request.approved:
                    team_request.status_label = "Approved"
                else:
                    team_request.status_label = "Denied"
            else:
                team_request.status_label = "Pending"
    else:
        manager_team_requests = []

    admin_profiles_to_process = None
    if request.user.is_staff:
        admin_profiles_to_process = 0
        for profile_record in Profile.objects.all():
            needs_team = profile_record.team is None
            needs_employment_date = profile_record.employment_date is None
            needs_vacation_days = profile_record.vacation_days <= 0
            if needs_team or needs_employment_date or needs_vacation_days:
                admin_profiles_to_process += 1

    return render(
        request,
        "myDesk/index.html",
        {
            "request_form": RequestForm(user=request.user),
            "my_requests": my_requests,
            "user_summary": user_summary,
            "manager_team_requests": manager_team_requests,
            "manager_pending_requests": manager_pending_requests,
            "manager_usage": manager_usage,
            "admin_profiles_to_process": admin_profiles_to_process,
            "team": profile.team,
            "profile": profile,
        },
    )


@login_required
def add_request(request):
    if request.method == "POST":
        form = RequestForm(request.POST, user=request.user)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.request_user = request.user.profile
            new_request.approved = False
            new_request.processed = False
            new_request.save()
    return HttpResponseRedirect(reverse("index"))


@login_required
@csrf_exempt
def edit_request(request):
    data = json.loads(request.body)
    request_id = data.get("request_id")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    vacation_request = Request.objects.get(pk=request_id,request_user=request.user.profile,)


    form_data = {
        "start_date": start_date,
        "end_date": end_date,
    }
    form = RequestForm(form_data, instance=vacation_request, user=request.user)
    if form.is_valid():
        form.save()
        return JsonResponse(vacation_request.serialize())

    return JsonResponse({"error": "Invalid data"}, status=400)


@login_required
@csrf_exempt
def delete_request(request):
    data = json.loads(request.body)
    request_id = data.get("request_id")
    vacation_request = Request.objects.get(pk=request_id,request_user=request.user.profile,)
    vacation_request.delete()
    return JsonResponse({"success": True})


@login_required
@csrf_exempt
def update_request_status(request):
    profile = request.user.profile
    data = json.loads(request.body)
    request_id = data.get("request_id")
    decision = data.get("decision")
    manager_message = data.get("manager_message", "")
    vacation_request = Request.objects.get(pk=request_id,request_user__team=profile.team,)
    vacation_request.manager_message = manager_message
    vacation_request.processed = True
    if decision == "approve":
        vacation_request.approved = True
    else:
        vacation_request.approved = False
    vacation_request.save()

    return JsonResponse(vacation_request.serialize())
