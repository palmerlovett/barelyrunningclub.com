from django.shortcuts import render
from .models import Meetup
from django_project import settings

# Create your views here.
def meetups(request):
	
	this_week = Meetup.objects.order_by("-date").first()


	meetup = this_week
	data = {
		"pagetitle_verbose": "Weekly Meetups at "+settings.CO_NAME,
		"gmap_query": meetup.location.gmap_query,
		"meetup": meetup }

	return render(request, 'upcoming/meetups.html', data)