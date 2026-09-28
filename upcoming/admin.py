# admin/upcoming.py
from django.contrib import admin

from .models import City, Meetup, Location, Event
from media.models import Flyer, EventFlyer, LocationLogo, LocationRoute

class FlyerInline(admin.StackedInline):
	model = Flyer
	fk_name = "meetup"
	fields = ("file",)
	extra = 0
	min_num = 1
	max_num = 1
	validate_min = True
	validate_max = True
	can_delete = False

class LocationLogoInline(admin.StackedInline):
	model = LocationLogo
	fk_name = "location"
	fields = ("file",)
	extra = 0
	min_num = 1
	max_num = 1
	validate_min = True
	validate_max = True
	can_delete = False

class LocationRouteInline(admin.StackedInline):
	model = LocationRoute
	fk_name = "location"
	fields = ("file",)
	extra = 0
	min_num = 0
	max_num = 1
	validate_min = True
	validate_max = True
	can_delete = False

class EventFlyerInline(FlyerInline):
    model = EventFlyer
    fk_name = "event"

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
	autocomplete_fields = ("city",)
	inlines = [LocationLogoInline, LocationRouteInline]




@admin.register(Meetup)
class MeetupTypeAdmin(admin.ModelAdmin):
	list_display = ("meetup_title", "meetup_date")
	search_fields = ("meetup__title", "meetup__content")
	inlines = [FlyerInline]

	def meetup_title(self, obj):
		return obj.title
	
	@admin.display(
		description="Date",
		ordering="meetup__date",)

	def meetup_date(self, obj):
		return obj.date




@admin.register(Event)
class EventTypeAdmin(admin.ModelAdmin):
	list_display = ("event_title", "event_date")
	search_fields = ("event__title", "event__content")
	inlines = [EventFlyerInline]

	def event_title(self, obj):
		return obj.title
	
	@admin.display(
		description="Date",
		ordering="event__date",)

	def event_date(self, obj):
		return obj.date

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
  search_fields = ("name",)
  def has_module_permission(self, request):
    return False