from django.shortcuts import render
from .models import Meetup, Event
from django_project import settings

# Create your views here.
def meetups(request):
	
	this_week = Meetup.objects.order_by("-date").first()


	meetup = this_week
	data = {
		"pageclass": "meetups",
		"pagetitle_verbose": "Weekly Meetups at "+settings.CO_NAME,
		"gmap_query": meetup.location.gmap_query,
		"meetup": meetup }

	return render(request, 'upcoming/meetups.html', data)

def events(request):
	
	upcoming = Event.objects.order_by("-date").first()


	event = upcoming
	data = {
		"pageclass": "events",
		"pagetitle_verbose": "Upcoming Events at "+settings.CO_NAME,
		"gmap_query": event.location.gmap_query,
		"meetup": event }

	return render(request, 'upcoming/meetups.html', data)