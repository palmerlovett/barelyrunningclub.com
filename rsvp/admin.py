# rsvp/admin.py
from django.contrib import admin
from upcoming.models import Event
from .models import Reservation


class LatestEventFilter(admin.SimpleListFilter):
  title = "event"
  parameter_name = "event"

  def lookups(self, request, model_admin):
    events = Event.objects.order_by("-date")[:50]
    return [("all", "All events")] + [(str(e.event_id), str(e)) for e in events]

  def queryset(self, request, queryset):
    if self.value() == "all":
      return queryset
    if self.value():
      return queryset.filter(event_id=self.value())
    latest = Event.objects.order_by("-date").first()
    return queryset.filter(event_id=latest.event_id) if latest else queryset

  def choices(self, changelist):
    latest = Event.objects.order_by("-date").first()
    for lookup, title in self.lookup_choices:
      is_default = self.value() is None and latest and lookup == str(latest.event_id)
      yield {
        "selected": self.value() == lookup or is_default,
        "query_string": changelist.get_query_string({self.parameter_name: lookup}),
        "display": f"{title} (latest)" if is_default else title,
      }


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
  list_display = ("member", "event", "created_at")
  list_filter = (LatestEventFilter, "member__verified")
  search_fields = ("member__full_name", "member__email", "event__title")