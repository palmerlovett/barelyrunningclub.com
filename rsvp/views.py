from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from upcoming.models import Event
from club.models import Member, Notification
from club.forms import MemberForm
from .models import Reservation



def rsvp(request, date=None):
  if date is None:
    event = Event.objects.order_by("-date").first()
  else:
    event = get_object_or_404(Event, date=date)

  member = Member.get_member_from_cookie(request)
  
  if request.method == "POST":
    redirect_member = None

    # Handle Resend Verification Request
    if member and "resend_verification" in request.POST:
      if not member.verified:
        member.send_verification_email(request=request)
      redirect_member = member

    elif member and "quick" in request.POST:
      # One-click RSVP for any recognized returning member. Identity comes
      # only from the signed cookie — never trust a member_id in the POST body.
      Reservation.objects.get_or_create(member=member, event=event)
      Notification.objects.create(
        recipient=member,
        verb="RSVP recieved. let go run.",)
      if not member.verified:
        member.send_verification_email(request=request)
      redirect_member = member

    else:
      form = MemberForm(request.POST)
      if form.is_valid():
        new_member, created = Member.objects.get_or_create(
          email=form.cleaned_data["email"],
          defaults={
            "full_name": form.cleaned_data["full_name"],
            "phone": form.cleaned_data["phone"],
            "dob": form.cleaned_data["dob"],
          },
        )

        Reservation.objects.get_or_create(member=new_member, event=event)

        if not new_member.verified:
          new_member.send_verification_email(request=request)

        redirect_member = new_member

    if redirect_member:
      if date:
        redirect_url = reverse("rsvp:signin", kwargs={"date": date})
      else:
        redirect_url = reverse("rsvp:recent")

      response = redirect(redirect_url)
      return redirect_member.set_member_cookie(response)

  else:
    form = MemberForm()

  if member:
    member._rsvp_event = event

  response = render(request, "rsvp/signup.html", {
    "event": event,
    "form": form,
    "member": member,
    "pageclass": 'rsvp'
  })
  return member.set_member_cookie(response) if member else response