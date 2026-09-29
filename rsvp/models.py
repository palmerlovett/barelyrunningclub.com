# rsvp/models.py

from django.db import models

class Reservation(models.Model):
  reservation_id = models.AutoField(primary_key=True)
  member = models.ForeignKey("club.Member", on_delete=models.CASCADE, related_name="reservations")
  event = models.ForeignKey("upcoming.Event", on_delete=models.CASCADE, related_name="reservations")
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = ("member", "event")

  def __str__(self):
    return f"{self.member.full_name} -> {self.event}"