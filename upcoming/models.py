from django.db import models

class Event(models.Model):
  event_id = models.AutoField(primary_key=True)
  title = models.CharField(max_length=200)
  flyer = models.ForeignKey(
    "media.Flyer",
    on_delete=models.PROTECT,
    related_name="events", )
  date = models.DateField()
  content = models.TextField(blank=True)

  class Meta:
    abstract = True

class Special(models.Model):
  event = models.OneToOneField(
    Event,
    on_delete=models.CASCADE,
    primary_key=True,)

class Meetup(models.Model):
  event = models.OneToOneField(
    Event,
    on_delete=models.CASCADE,
    primary_key=True,)