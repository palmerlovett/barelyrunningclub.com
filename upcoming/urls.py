# upcoming/urls.py
from django.urls import path
from . import views

app_name = "upcoming"

urlpatterns = [
  path("meetups/", views.meetups, name="meetup"),
  path("events/", views.events, name="events"),
]