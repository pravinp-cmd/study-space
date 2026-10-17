import calendar as pycalendar
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout as auth_logout
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    DAYS,
    DailyRating,
    StudentNote,
    StudentProfile,
    StudyAlarm,
    StudySession,
)


def get_profile(request):
    if not request.session.session_key:
        request.session.create()

    profile, _ = StudentProfile.objects.get_or_create(
        session_key=request.session.session_key
    )
    return profile


@login_required
def home(request):
    profile = get_profile(request)

    try:
        active_day = int(
            request.GET.get("day", timezone.localdate().weekday())
        )
        active_day = max(0, min(6, active_day))
    except (TypeError, ValueError):
        active_day = timezone.localdate().weekday()

    all_sessions = list(profile.sessions.all())
    per_day = []

    for number, name in DAYS:
        day_sessions = [session for session in all_sessions if session.day == number]
        planned = sum(session.duration_minutes for session in day_sessions)
        completed = sum(
            session.duration_minutes
            for session in day_sessions
            if session.completed
        )

        per_day.append({
            "name": name,
            "planned_minutes": planned,
            "completed_minutes": completed,
        })

    max_planned = max(
        (item["planned_minutes"] for item in per_day),
        default=0,
    )

    for item in per_day:
        item["planned_pct"] = (
            round(item["planned_minutes"] * 100 / max_planned)
            if max_planned else 0
        )
        item["completed_pct"] = (
            round(item["completed_minutes"] * 100 / max_planned)
            if max_planned else 0
        )

    today = timezone.localdate()
    rating = profile.ratings.filter(day=today).first()

    alarm_data = [
        {
            "id": alarm.id,
            "time": alarm.time.strftime("%H:%M"),
            "label": alarm.label,
            "enabled": alarm.enabled,
        }
        for alarm in profile.alarms.all()
    ]

    total_minutes = sum(item["planned_minutes"] for item in per_day)

    context = {
        "profile": profile,
        "days": DAYS,
        "active_day": active_day,
        "active_day_name": dict(DAYS).get(active_day, ""),
        "sessions": [
            session for session in all_sessions
            if session.day == active_day
        ],
        "session_count": len(all_sessions),
        "subject_count": len({
            session.subject.casefold()
            for session in all_sessions
        }),
        "total_hours": total_minutes / 60,
        "per_day": per_day,
        "alarms": profile.alarms.all(),
        "alarm_data": alarm_data,
        "today_rating": rating.stars if rating else 0,
    }

    return render(request, "home.html", context)


@login_required
@require_POST
def add_session(request):
    profile = get_profile(request)

    try:
        day = int(request.POST.get("day", ""))
        valid_days = {int(number) for number, _ in DAYS}

        subject = request.POST.get("subject", "").strip()[:100]
        topic = request.POST.get("topic", "").strip()[:200]

        start_value = request.POST.get("start_time", "")
        end_value = request.POST.get("end_time", "")

        start_time = datetime.strptime(start_value, "%H:%M").time()
        end_time = datetime.strptime(end_value, "%H:%M").time()

        if day not in valid_days:
            raise ValueError("Invalid day")

        if not subject or not topic:
            messages.error(request, "Subject and topic are required.")
        elif end_time <= start_time:
            messages.error(request, "End time must be after start time.")
        else:
            StudySession.objects.create(
                profile=profile,
                day=day,
                subject=subject,
                topic=topic,
                start_time=start_time,
                end_time=end_time,
            )
            messages.success(request, "Study session added.")

    except (TypeError, ValueError):
        messages.error(request, "Check the day and start/end times.")
        return redirect("home")

    return redirect(f"/?day={day}")


@login_required
@require_POST
def toggle_session(request, session_id):
    session = get_object_or_404(
        StudySession,
        id=session_id,
        profile=get_profile(request),
    )
    session.completed = not session.completed
    session.save(update_fields=["completed"])
    return redirect(f"/?day={session.day}")


@login_required
@require_POST
def delete_session(request, session_id):
    session = get_object_or_404(
        StudySession,
        id=session_id,
        profile=get_profile(request),
    )
    day = session.day
    session.delete()
    return redirect(f"/?day={day}")


@login_required
def profile(request):
    profile = get_profile(request)

    if request.method == "POST":
        profile.name = request.POST.get("name", "").strip()[:60]
        profile.grade = request.POST.get("grade", "").strip()[:40]
        profile.save(update_fields=["name", "grade"])
        messages.success(request, "Profile saved.")
        return redirect("profile")

    return render(request, "profile.html", {"profile": profile})


@login_required
@require_POST
def save_profile(request):
    profile = get_profile(request)
    profile.name = request.POST.get("name", "").strip()[:60]
    profile.grade = request.POST.get("grade", "").strip()[:40]
    profile.save(update_fields=["name", "grade"])
    messages.success(request, "Profile saved.")
    return redirect("profile")


@login_required
def profile_page(request):
    profile = get_profile(request)
    return render(request, "profile.html", {"profile": profile})


@login_required
def calculator_page(request):
    return render(request, "calculator.html")


@login_required
def calendar_page(request):
    today = timezone.localdate()

    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))

        if month not in range(1, 13) or year not in range(1900, 9999):
            raise ValueError
    except (TypeError, ValueError):
        year, month = today.year, today.month

    profile = get_profile(request)

    sessions_by_weekday = {day: [] for day in range(7)}
    for session in profile.sessions.all().order_by("start_time"):
        sessions_by_weekday[session.day].append(session)

    weeks = []
    month_calendar = pycalendar.Calendar(firstweekday=0)

    for week_dates in month_calendar.monthdatescalendar(year, month):
        week = []

        for day_date in week_dates:
            in_month = day_date.month == month
            week.append({
                "date": day_date,
                "in_month": in_month,
                "is_today": day_date == today,
                "sessions": (
                    sessions_by_weekday[day_date.weekday()]
                    if in_month else []
                ),
            })

        weeks.append(week)

    previous_month = date(year, month, 1) - timedelta(days=1)
    next_month = (date(year, month, 1) + timedelta(days=32)).replace(day=1)

    return render(request, "calendar.html", {
        "weeks": weeks,
        "month_name": pycalendar.month_name[month],
        "year": year,
        "previous_year": previous_month.year,
        "previous_month": previous_month.month,
        "next_year": next_month.year,
        "next_month": next_month.month,
    })


@login_required
def notes_page(request):
    profile = get_profile(request)
    return render(request, "notes.html", {
        "notes": profile.notes.all(),
    })


@login_required
@require_POST
def add_note(request):
    title = request.POST.get("title", "").strip()[:120]
    content = request.POST.get("content", "").strip()

    if content:
        StudentNote.objects.create(
            profile=get_profile(request),
            title=title or "Untitled note",
            content=content,
        )
        messages.success(request, "Note added.")
    else:
        messages.error(request, "Note content cannot be empty.")

    return redirect("notes")


@login_required
@require_POST
def delete_note(request, note_id):
    note = get_object_or_404(
        StudentNote,
        id=note_id,
        profile=get_profile(request),
    )
    note.delete()
    return redirect("notes")


@login_required
@require_POST
def add_alarm(request):
    profile = get_profile(request)

    try:
        alarm_time = datetime.strptime(
            request.POST.get("time", ""),
            "%H:%M",
        ).time()
        label = (
            request.POST.get("label", "").strip()
            or "Study reminder"
        )

        StudyAlarm.objects.create(
            profile=profile,
            time=alarm_time,
            label=label,
        )
        messages.success(request, "Reminder added.")

    except (TypeError, ValueError):
        messages.error(request, "Enter a valid alarm time.")

    return redirect("home")


@login_required
@require_POST
def toggle_alarm(request, alarm_id):
    alarm = get_object_or_404(
        StudyAlarm,
        id=alarm_id,
        profile=get_profile(request),
    )
    alarm.enabled = not alarm.enabled
    alarm.save(update_fields=["enabled"])
    return redirect("home")


@login_required
@require_POST
def delete_alarm(request, alarm_id):
    alarm = get_object_or_404(
        StudyAlarm,
        id=alarm_id,
        profile=get_profile(request),
    )
    alarm.delete()
    return redirect("home")


@login_required
@require_POST
def rate_day(request):
    try:
        stars = int(request.POST.get("stars", ""))

        if stars not in range(1, 6):
            raise ValueError

    except (TypeError, ValueError):
        messages.error(request, "Choose a rating from 1 to 5.")
        return redirect("home")

    DailyRating.objects.update_or_create(
        profile=get_profile(request),
        day=timezone.localdate(),
        defaults={"stars": stars},
    )
    return redirect("home")


@login_required
def rough_page(request):
    return render(request, "rough.html")


@require_POST
def logout_page(request):
    auth_logout(request)
    return redirect("logout_done")


def logout_done_page(request):
    return render(request, "logout.html")


def signup(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "signup.html", {"form": form})