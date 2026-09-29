# cms/utils.py

from django.apps import apps
from django.template import Origin, engines, Template, Context
from django.template.loaders.base import Loader
from django.template import TemplateDoesNotExist


class DatabaseLoader(Loader):
  prefixes = ("cms/", "app/")
  
  def get_template_sources(self, template_name):
    if template_name.startswith(self.prefixes):
      yield Origin(
        name=template_name,
        template_name=template_name,
        loader=self,)
  
  def get_contents(self, origin):
    template_name = origin.template_name
    prefix = next(
      (p for p in self.prefixes if template_name.startswith(p)),
      None,)
    if prefix is None:
      raise TemplateDoesNotExist(template_name)
    path = template_name.removeprefix(prefix)

    TemplateModel = apps.get_model("cms", "Template")
    print(f'path {path}')

    Model = apps.get_model("cms", "Page" if prefix == "app/" else "Template")
    try:
      return Model.objects.get(path=path).source
    except Model.DoesNotExist:
      raise TemplateDoesNotExist(template_name)

from django.template import Template, Context

def pre_render(content_string, context=None):
  template = Template(content_string)
  if isinstance(context, Context):
    return template.render(context)
  return template.render(Context(context or {}))

def cms_url(page_name):
  from .models import Page
  """
  Returns the URL for a page with the given name

  Args:
    page_name: The name of the page to look up

  Returns:
    The full_slug URL path for the page, or None if not found
  """
  try:
    page = Page.objects.get(name__iexact=page_name)
    return page.full_slug
  except Page.DoesNotExist:
    return None