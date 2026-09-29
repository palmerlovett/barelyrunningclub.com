import uuid
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


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

  def __str__(self):
    return self.full_name

  def send_verification_email(self, request=None):
    verify_path = reverse('club:verify-email', args=[str(self.verification_token)])
    verify_url = request.build_absolute_uri(verify_path) if request else f"https://{settings.CO_DOMAIN}{verify_path}"

    send_mail(
      subject=f"Verify your email for {settings.CO_NAME}",
      message=(
        f"Hi {self.full_name},\n\n"
        f"Please verify your email by clicking the link below:\n{verify_url}\n\n"
        f"If you didn't request this, you can ignore this message."
      ),
      from_email=settings.DEFAULT_FROM_EMAIL,
      recipient_list=[self.email],
    )

  def verify(self):
    if not self.verified:
      self.verified = True
      self.save(update_fields=["verified"])

  @property
  def has_rsvp(self):
    # Set by the view (member._rsvp_event = event) before rendering, so this
    # can be used directly in templates as {{ member.has_rsvp }} without args.
    event = getattr(self, "_rsvp_event", None)
    return bool(event) and self.reservations.filter(event=event).exists()