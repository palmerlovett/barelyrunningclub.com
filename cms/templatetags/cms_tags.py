
from django import template
from cms.utils import cms_url as cms_url_util

register = template.Library()

@register.simple_tag
def cms_url(page_name):
  ## USAGE: {% cms_url '{{page_name}}' %}
  return cms_url_util(page_name)

@register.simple_tag
def part(part_name):
  from cms.models import Part
  from cms.utils import pre_render
  part = Part.objects.get(name__iexact=part_name)
  return pre_render(part.content)

@register.simple_tag
def media(type_loc, file="", output='html'):
  from django.utils.safestring import mark_safe
  # USAGE media 'photo:album' 'photo_name'
  #    OR media 'file:folder' 'file_name'
  type_loc = type_loc.split(':')
  type = type_loc[0] #photo or file (which model to look for)
  loc = type_loc[1] #location of file

  def output_image_html(url, title):
    return mark_safe(f'<img src="{url}" alt="{title}" title="{title}">')
  
  if type == 'photo':
    from photo_book.models import Photo
    try:
      photo = Photo.objects.get(album__title__iexact=loc, title__iexact=file)
    except: return 'photo not found'
    if output == 'url':
      return photo.image.url
    if output == 'html':
      return output_image_html(photo.image.url, photo.title)


  def weblink_html(doc):
    return f'<li class="weblink"><a target="_blank" href="{doc.weblink}">{doc.title}</a>'
  def document_html(doc):
    ext = doc.doc.url.split('.')[-1]
    if ext in ('svg', 'png', 'jpg', 'gif'):
      return output_image_html(doc.doc.url, doc.title)
    else:
      return f'<li class="document"><a target="_blank" href="{doc.doc.url}">{doc.title}</a>'
  def alias_html(doc):
    return f'<li class="document"><a target="_blank" href="{doc.alias.doc.url}">{doc.title}</a>'
  
  from cloud.models import File

  if type == 'folder':
    if loc.isdigit():      
      try: docs = File.objects.filter(folder__folder_id=loc)
      except: return 'folder id not found'
    else:
      try:
        docs = File.objects.filter(folder__folder_path__iexact=loc, listed=True)
        docs.order_by('order')
      except: return 'folder path not found'

    html_output = '<ul class="media">'
    for doc in docs:
      if doc.file_type == 'weblink':
        html_output += weblink_html(doc)
      if doc.file_type == 'document':
        html_output += document_html(doc)
      if doc.file_type == 'alias':
        html_output += alias_html(doc)
    html_output += '</ul>'
    return mark_safe(html_output)
  
  if type == 'file':
    if loc.isdigit(): 
      try: doc = File.objects.get(file_id=loc)
      except: return 'file id not found'
    else:
      try:
        doc = File.objects.get(filepath__iexact=loc)  
      except: return 'file path not found'

    if doc.file_type == 'photo':
      if output == 'html':
        return mark_safe(output_image_html(doc.photo.image.url, doc.title))
      else: return doc.photo.image.url
    if doc.file_type == 'weblink':
      if output == 'html':
        return mark_safe(weblink_html(doc))
      else: return doc.weblink
    if doc.file_type == 'document':
      if output == 'html':
        return mark_safe(document_html(doc))
      else: return doc.doc.url
    if doc.file_type == 'alias':
      if output == 'html':
        return mark_safe(alias_html(doc))
      else: return doc.alias.doc.url
