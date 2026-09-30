# club/models.py
import uuid
from django.db import models
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.signing import BadSignature



class Member(models.Model):
  member_id = models.AutoField(primary_key=True)
  email = models.EmailField(unique=True)
  full_name = models.CharField(max_length=200)
  phone = models.CharField(max_length=20, blank=True, default="")
  dob = models.DateField(null=True, blank=True)
  verified = models.BooleanField(default=False)
  verification_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
  joined_at = models.DateTimeField(auto_now_add=True)

  @property
  def first_name(self):
    parts = self.full_name.split()
    return parts[0] if parts else ""

  @property
  def last_name(self):
    parts = self.full_name.split()
    return " ".join(parts[1:]) if len(parts) > 1 else ""

  def get_member_from_cookie(request):
    try:
      member_id = request.get_signed_cookie("member_id")
    except (KeyError, BadSignature):
      return None
    return Member.objects.filter(pk=member_id).first()

  def set_member_cookie(self, response):

    # Re-issuing on every visit rolls the 400-day window forward, so a member
    # who visits at least once a year effectively never gets logged out.
    response.set_signed_cookie('member_id', self.member_id, max_age=(60 * 60 * 24 * 400))
    return response

  def send_verification_email(self, request=None):
    verify_path = reverse('club:verify-email', args=[str(self.verification_token)])
    verify_url = request.build_absolute_uri(verify_path) if request else f"https://{settings.CO_DOMAIN}{verify_path}"

    context = {"member": self, "verify_url": verify_url, "CO_NAME": settings.CO_NAME, "SITE_URL": settings.SITE_URL}
    text_body = render_to_string("club/emails/verify_email.txt", context)
    html_body = render_to_string("club/emails/verify_email.html", context)

    email = EmailMultiAlternatives(
      subject=f"Verify your RSVP @ {settings.CO_NAME}",
      body=text_body,
      from_email=settings.DEFAULT_FROM_EMAIL,
      to=[self.email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send()
    Notification.objects.create(
      recipient=self,
      verb="an email with a verification link has been sent",)


  def verify(self):
    if not self.verified:
      self.verified = True
      self.save(update_fields=["verified"])
      Notification.objects.create(
        recipient=self,
        verb="email has been verified")

  @property
  def has_rsvp(self):
    # Set by the view (member._rsvp_event = event) before rendering, so this
    # can be used directly in templates as {{ member.has_rsvp }} without args.
    event = getattr(self, "_rsvp_event", None)
    return bool(event) and self.reservations.filter(event=event).exists()

  def __str__(self):
    return self.full_name


class Notification(models.Model):
  recipient = models.ForeignKey(
    Member,
    on_delete=models.CASCADE,
    related_name="notifications",
  )
  # Set null=True to support system-generated alerts without a specific actor
  actor = models.ForeignKey(
    Member,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="actions_triggered",
  )
  verb = models.CharField(max_length=255)
  target_url = models.CharField(max_length=255, blank=True, default="")
  unread = models.BooleanField(default=True)
  timestamp = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-timestamp"]
    indexes = [
      models.Index(fields=["recipient", "unread"]),
    ]

  def __str__(self):
    actor_name = self.actor.full_name if self.actor else "System"
    return f"{actor_name} {self.verb} -> {self.recipient.full_name}"