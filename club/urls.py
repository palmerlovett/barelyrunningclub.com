# club/urls.py

from django.urls import path
from . import views

app_name = 'club'

urlpatterns = [
  path('verify/<uuid:token>/', views.verify_email, name='verify-email'),
]