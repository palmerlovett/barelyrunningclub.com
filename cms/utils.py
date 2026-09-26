from django.apps import apps
from django.template import Origin, engines
from django.template.loaders.base import Loader

class DatabaseLoader(Loader):
  prefix = "cms/"
  def get_template_sources(self, template_name):
    if template_name.startswith(self.prefix):
      yield Origin(
        name=template_name,
        template_name=template_name,
        loader=self,)

  def get_contents(self, origin):
    TemplateModel = apps.get_model("cms", "Template")
    name = origin.template_name.removeprefix(self.prefix)
    try:
      stored_template = TemplateModel.objects.get(name=name)
    except TemplateModel.DoesNotExist:
      raise TemplateDoesNotExist(origin.template_name)
    
    return stored_template.source

def pre_render(template_string, context_dict=None, request=None):
  template = engines["django"].from_string(template_string)
  rendered = template.render(context_dict or {}, request=request)
  return rendered


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