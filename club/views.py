# club/views.py

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Member

def verify_email(request, token):
  member = get_object_or_404(Member, verification_token=token)

  if member.verified:
    messages.info(request, "This email is already verified.")
  else:
    member.verify()
    messages.success(request, "Your email has been verified. Welcome!")

  return render(request, 'club/verified.html', {"member": member})