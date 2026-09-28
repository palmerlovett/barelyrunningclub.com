from django.shortcuts import render
from .models import Meetup

# Create your views here.
def meetups(request):
	
	this_week = Meetup.objects.order_by("-date").first()


	meetup = this_week
	data = {
		"gmap_query": meetup.location.gmap_query,
		"meetup": meetup }

	return render(request, 'upcoming/meetups.html', data)