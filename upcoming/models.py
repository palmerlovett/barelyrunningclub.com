# upcoming/models.py

from django.db import models
from datetime import time as dt_time

class City(models.Model):
  city_id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=100)

  def __str__(self):
    return self.name

  class Meta:
    verbose_name = "City"
    verbose_name_plural = "Cities"

class Location(models.Model):
  location_id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=100)
  city = models.ForeignKey(City, on_delete=models.SET_NULL,
    null=True)

  @property
  def gmap_query(self):
    gmap_query = self.name
    if self.city:
      gmap_query = gmap_query.replace(self.city.name, "")
    gmap_query = gmap_query.replace(" ", "%20").replace(",", "%2c")
    gmap_query += '%2c%20'
    gmap_query += self.city.name.replace(" ", "%20").replace(",", "%2c")
    
    return gmap_query

  def __str__(self):
    return self.name

class Event(models.Model):
  event_id = models.AutoField(primary_key=True)
  title = models.CharField(max_length=200)
  location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
  date = models.DateField()
  description = models.TextField(blank=True)

  def __str__(self):
    return f'{self.title}, {self.date}'

  class Meta:
    ordering = ['-date']

class SpecialEvent(Event):
  event_ptr = models.OneToOneField(
    Event, on_delete=models.CASCADE,
    parent_link=True, primary_key=True )
  time = models.TimeField(default=dt_time(18, 0),
    blank=True, null=True)

class Meetup(Event):
  event_ptr = models.OneToOneField(
    Event, on_delete=models.CASCADE,
    parent_link=True, primary_key=True )