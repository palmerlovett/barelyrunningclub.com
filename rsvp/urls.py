# rsvp/urls.py

from django.urls import path
from . import views

app_name = "rsvp"

urlpatterns = [
  path("", views.rsvp, name="recent"),
  path("<str:date>/", views.rsvp, name="signin"),
]