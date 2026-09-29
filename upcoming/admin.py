# upcoming/admin.py

from django.contrib import admin
from django import forms
from .models import City, Meetup, Location, SpecialEvent
from media.models import Flyer, LocationLogo, LocationRoute

class FlyerInline(admin.StackedInline):
	model = Flyer
	fk_name = "event"
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


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
	autocomplete_fields = ("city",)
	inlines = [LocationLogoInline, LocationRouteInline]


class MeetupAdminForm(forms.ModelForm):
  class Meta:
    model = Meetup
    fields = '__all__'
    widgets = {
      'time': forms.TimeInput(attrs={'type': 'time', 'step': '60'}),
    }

@admin.register(Meetup)
class MeetupTypeAdmin(admin.ModelAdmin):
	list_display = ("meetup_title", "meetup_date")
	search_fields = ("title", "description")
	admin_caching_enabled = False
	inlines = [FlyerInline]
	form = MeetupAdminForm

	def meetup_title(self, obj):
		return obj.title
	
	@admin.display(
		description="Date",
		ordering="date",)

	def meetup_date(self, obj):
		return obj.date


@admin.register(SpecialEvent)
class EventTypeAdmin(admin.ModelAdmin):
	list_display = ("event_title", "event_date")
	search_fields = ("title", "description")
	admin_caching_enabled = False
	inlines = [FlyerInline]

	def event_title(self, obj):
		return obj.title
	
	@admin.display(
		description="Date",
		ordering="date",)

	def event_date(self, obj):
		return obj.date

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
  search_fields = ("name",)
  def has_module_permission(self, request):
    return False