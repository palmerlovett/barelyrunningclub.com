from django.template import loader, engines
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.safestring import mark_safe
from .models import Alias, Page
from django.utils.text import slugify
from .utils import pre_render
from django.shortcuts import redirect

def page(request):

  #try getting page with by matching request.path to Page.path
  if request.path == "/":
    try:
      page = Page.objects.get(name__iexact="index", public=True)
    except Page.DoesNotExist:
      raise Http404("Home page is not configured or not public")
  else:
    try:
      page = Page.objects.get(path=request.path, public=True)
    except Page.DoesNotExist:
      try:
        alias = Alias.objects.select_related("destination").get(path=request.path)
      except Alias.DoesNotExist:
        print(f"tried to access nonexistent Page: {request.path}")
        raise Http404
      print(f"redirecting to {alias.destination.path}...")
      return redirect(alias.destination.path, permanent=True)

  pagetitle = page.name
  pageclass = 'cms '+slugify(page.name)

  canon = settings.SITE_URL+page.path

  data = {
    "canon": canon,
    "page": page,
    "content": page.content,
    "page_desc": page.desc,
    "pagetitle": page.name,
    "pageclass": pageclass
  }
  
  print(f'\n\n\nextra extra content: {page.source}\n\n')

  html = pre_render(page.source, data, request)
  # page.content until we solve the rendering issue 

  print(f'\n\n\nextra extra html: {html}\n\n')
  
  return HttpResponse(html)