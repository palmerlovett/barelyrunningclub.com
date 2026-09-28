from django.urls import path
from . import views

app_name = 'upcoming'

urlpatterns = [
  path('', views.meetups, name="meetup"),
]