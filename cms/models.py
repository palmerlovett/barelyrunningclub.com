from django.db import models
from django.utils.text import slugify
from cms.utils import pre_render

# Create your models here.

class Template(models.Model):
  template_id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=100)
  content = models.TextField(default="", blank=True)
  source = models.TextField(default="", blank=True, editable=False)
  parent_template = models.ForeignKey('self', on_delete=models.SET_NULL,
    null=True, blank=True)

  path = models.CharField(max_length=255, editable=False,
    null=True, blank=True)
  display_name = models.CharField(max_length=100, editable=False,
    null=True, blank=True)

  def save(self, *args, **kwargs):

    names = [self.name]
    paths = [slugify(self.name)]
    ancestor = self.parent_template
    visited = set()

    while ancestor:
      if ancestor.pk in visited:
        raise ValueError("Circular page hierarchy detected.")

      visited.add(ancestor.pk)
      names.insert(0, ancestor.name)
      paths.insert(0, slugify(ancestor.name))
      ancestor = ancestor.parent_template


    path = "/".join(paths)
    self.display_name = " / ".join(names)
    print(f'path {path}')

    wrapped_content = self.content
    if self.parent_template:
      wrapped_content  = '{% extends "cms/'+self.parent_template.path+'" %}\n'
      wrapped_content += "{% block content %}\n"
      wrapped_content += "{{ block.super }}\n"
      wrapped_content += self.content
      wrapped_content += "\n{% endblock %}"
    
    self.source = wrapped_content
    self.path = path

    print(f'path: {self.path}')

    super().save(*args, **kwargs)

  def __str__(self):
    return self.display_name

  class Meta:
    ordering = [
      models.Case(
        models.When(parent_template__isnull=True, then=models.Value(0)),
        default=models.Value(1),
        output_field=models.IntegerField(),
      ),
      "display_name",]


class Part(models.Model):
  part_id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=100)
  content = models.TextField()

  def __str__(self):
    return self.name

  class Meta:
    ordering = ["name"]

class Page(models.Model):
  page_id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=100)
  slug = models.CharField(max_length=100, blank=True, null=True, default="")
  path = models.CharField(max_length=250, blank=True, null=True, default="", editable=False)
  
  template = models.ForeignKey(Template,on_delete=models.SET_NULL,
    null=True, blank=True,
    help_text="choose which template to extend")
  
  parent_page = models.ForeignKey('self',
    blank=True, null=True, default="",
    on_delete=models.SET_NULL,
    help_text="(optional)")
  
  desc = models.TextField(blank=True, null=True, default="")
  content = models.TextField(default="", blank=True)
  source = models.TextField(default="", blank=True, editable=False)

  public = models.BooleanField(default=False)

  last_mod = models.DateField(null=True, blank=True)
  display_name = models.CharField(max_length=250, blank=True, null=True, default="", editable=False)


  def save(self, *args, **kwargs):
    self.slug = slugify(self.slug or self.name)
    self.slug = "" if self.slug == 'index' else self.slug
    names = [self.name]
    slugs = [self.slug]
    ancestor = self.parent_page
    visited = set()

    if self.template:
      wrapped_content  = '{% extends "cms/'+self.template.path+'" %}\n'
      wrapped_content += "{% block content %}\n"
      wrapped_content += "{{ block.super }}\n"
      wrapped_content += self.content
      wrapped_content += "\n{% endblock %}"
    else:
      wrapped_content = self.content

    while ancestor:
      if ancestor.pk in visited:
        raise ValueError("Circular page hierarchy detected.")

      visited.add(ancestor.pk)
      names.insert(0, ancestor.name)
      slugs.insert(0, ancestor.slug)
      ancestor = ancestor.parent_page

    self.source = wrapped_content
    self.display_name = " / ".join(names)
    self.path = f'{"/".join(slugs)}'
    self.path = '/' if self.path == '//' else self.path
    print(f'path:: {self.path}')

    super().save(*args, **kwargs)

  def __str__(self):
    return self.display_name
    #if self.path == '/':
    #  return self.display_name
    #else: return f'{self.name} ({self.path})'

  class Meta:
    ordering = [
      models.Case(
        models.When(name__iexact="index", then=models.Value(0)),
        default=models.Value(1),
        output_field=models.IntegerField(),),
      "display_name",]

class Alias(models.Model):
  alias_id = models.AutoField(primary_key=True)
  path = models.CharField(max_length=100)
  destination = models.ForeignKey(Page, on_delete=models.CASCADE)

  def __str__(self):
    return f'{self.path} --> {self.destination.path}'

  def save(self, *args, **kwargs):
    path = (self.path or "").strip("/")
    self.path = f"/{path}/" if path else "/"
    super().save(*args, **kwargs)

  class Meta:
    verbose_name = "Alias"
    verbose_name_plural = "Alia"

class App(models.Model):
  app_id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=100)
  path = models.CharField(max_length=255, editable=False)
  source = models.TextField(default="", blank=True)

  template = models.ForeignKey(Template,
    null=True, blank=True,
    on_delete=models.SET_NULL)

  def save(self, *args, **kwargs):
    path = (self.path or "").strip("/")
    self.path = path


    wrapped_content = ""
    if self.template:
      wrapped_content  = '{% extends "cms/'+self.template.path+'" %}\n'
      wrapped_content += "{% block content %}\n"
      wrapped_content += "{{ block.super }}\n"
      wrapped_content += self.source
      wrapped_content += "\n{% endblock %}"
    else: print(f'no template')

    self.source = wrapped_content

    print(f'self source: {self.source}')
    super().save(*args, **kwargs)

  def __str__(self):
    return self.name