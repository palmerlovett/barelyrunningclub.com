# upcoming/urls.py
from django.urls import path, re_path
from . import views

app_name = "upcoming"

urlpatterns = [
  re_path(r'^meetup/(?P<date>\d{4}-\d{2}-\d{2})/$', views.meetups, name='past_meetup'),
  path("meetups/", views.meetups, name="meetup"),
  path("events/", views.events, name="events"),
]