from django.shortcuts import render
from django.http import Http404
from .models import Event, Meetup, SpecialEvent
from django_project import settings

def meetups(request, date=None):
  if date is None:
    qs = Meetup.objects.all()
  else:
    qs = Event.objects.all()
  
  if date:
    qs = qs.filter(date=date)

  base = qs.first()
  if base is None:
    raise Http404

  meetup = downcast(base) if date else base

  data = {
    "pageclass": "meetups",
    "pagetitle_verbose": "Weekly Meetups at " + settings.CO_NAME,
    "gmap_query": meetup.location.gmap_query,
    "event": meetup }

  return render(request, 'upcoming/meetups.html', data)


def events(request):
  event = SpecialEvent.objects.order_by("-date").first()
  if event is None:
    raise Http404

  data = {
    "pageclass": "events",
    "pagetitle_verbose": "Upcoming Events at " + settings.CO_NAME,
    "gmap_query": event.location.gmap_query,
    "event": event }

  return render(request, 'upcoming/events.html', data)


def downcast(base):
  """Given an Event instance, return the real SpecialEvent or Meetup it is."""
  try:
    return base.specialevent
  except SpecialEvent.DoesNotExist:
    try:
      return base.meetup
    except Meetup.DoesNotExist:
      return base