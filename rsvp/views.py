from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.signing import BadSignature
from upcoming.models import Event
from club.models import Member
from club.forms import MemberForm
from .models import Reservation

MEMBER_COOKIE = "member_id"
# 400 days is the practical ceiling — Chrome (and other Chromium browsers)
# silently clamp any longer Max-Age down to this, so anything bigger is wasted.
MEMBER_COOKIE_MAX_AGE = 60 * 60 * 24 * 400


def get_member_from_cookie(request):
  try:
    member_id = request.get_signed_cookie(MEMBER_COOKIE)
  except (KeyError, BadSignature):
    return None
  return Member.objects.filter(pk=member_id).first()


def set_member_cookie(response, member):
  # Re-issuing on every visit rolls the 400-day window forward, so a member
  # who visits at least once a year effectively never gets logged out.
  response.set_signed_cookie(MEMBER_COOKIE, member.member_id, max_age=MEMBER_COOKIE_MAX_AGE)
  return response


def rsvp(request, date=None):
  if date is None:
    event = Event.objects.order_by("-date").first()
  else:
    event = get_object_or_404(Event, date=date)

  member = get_member_from_cookie(request)

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

    # Redirect back to the same page
    if redirect_member:
      if date:
        redirect_url = reverse("rsvp:signin", kwargs={"date": date})
      else:
        redirect_url = reverse("rsvp:recent")

      response = redirect(redirect_url)
      return set_member_cookie(response, redirect_member)

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
  return set_member_cookie(response, member) if member else response