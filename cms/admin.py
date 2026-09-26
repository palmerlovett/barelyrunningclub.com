from django.contrib import admin
from .models import Alias, Template, Part, Page
from django_ace import AceWidget
from django import forms
from django.conf import settings


@admin.register(Alias)
class AliasAdmin(admin.ModelAdmin):
  list_display = ["path", "destination"]


class TemplateAdminForm(forms.ModelForm):
  class Meta:
    model = Page
    fields = '__all__'
    widgets = {
      'content': AceWidget(**settings.ACE_EDITOR_OPTIONS)
    }

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
	form = TemplateAdminForm
	list_display = ["display_name"]

class PageAdminForm(forms.ModelForm):
  class Meta:
    model = Page
    fields = '__all__'
    widgets = {
      'content': AceWidget(**settings.ACE_EDITOR_OPTIONS)
    }

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
  form = PageAdminForm
  list_display = ("display_name", "public",)
  search_field = ("name", "content",)

##@admin.register(Template)
##class TemplateAdmin(admin.ModelAdmin):
##  list_display = ("name", "template_path",)
##  search_field = ("name", "template_path",)

class PartAdminForm(forms.ModelForm):
  class Meta:
    model = Part
    fields = '__all__'
    widgets = {
      'content': AceWidget(**settings.ACE_EDITOR_OPTIONS)
    }

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
  form = PartAdminForm
  list_display = ("name",)
  search_field = ("name", "html",)