from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", views.home, name="home"),
    path("sessions/add/", views.add_session, name="add_session"),
    path("sessions/<int:session_id>/toggle/", views.toggle_session, name="toggle_session"),
    path("sessions/<int:session_id>/delete/", views.delete_session, name="delete_session"),
    path("profile/save/", views.save_profile, name="save_profile"),
    path("alarms/add/", views.add_alarm, name="add_alarm"),
    path("alarms/<int:alarm_id>/toggle/", views.toggle_alarm, name="toggle_alarm"),
    path("alarms/<int:alarm_id>/delete/", views.delete_alarm, name="delete_alarm"),
    path("rating/", views.rate_day, name="rate_day"),
    path("calculator/", views.calculator_page, name="calculator"),
    path("profile/", views.profile_page, name="profile"),
    path("calculator/", views.calculator_page, name="calculator"),
    path("calendar/", views.calendar_page, name="calendar"),
    path("notes/", views.notes_page, name="notes"),
    path("notes/add/", views.add_note, name="notes_add"),
    path("notes/<int:note_id>/delete/", views.delete_note, name="notes_delete"),
    path("rough/", views.rough_page, name="rough"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"),name="login",),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("logout/", views.logout_page, name="logout"),
    path("logged-out/", views.logout_done_page, name="logout_done"),
    path("signup/", views.signup, name="signup"),
]