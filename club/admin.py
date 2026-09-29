# club/admin.py

from django.contrib import admin
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
  list_display = ("full_name", "email", "phone", "verified", "joined_at")
  list_filter = ("verified",)
  search_fields = ("full_name", "email", "phone")
  readonly_fields = ("verification_token", "joined_at")