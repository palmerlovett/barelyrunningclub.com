# media/models.py
from django.db import models
import os
from imagefield.fields import ImageField
from django.utils.text import slugify
from django.conf import settings

from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


# Create your models here.

class File(models.Model):
  file_id = models.AutoField(primary_key=True)
  file = models.ImageField(upload_to="tmp/")
  uploaded_at = models.DateTimeField(auto_now_add=True)
  processed = models.BooleanField(default=False, editable=False)
  
  def generate_file_slug(self, format=None, name=None, folder='photos/'):
    stem, extension = os.path.splitext(os.path.basename(self.file.name))
    extension = ".jpg" if extension.lower() == ".jpeg" else extension.lower()
    stem = slugify(stem) or "image"
    name = stem if(name is None) else name
    return f"{folder.strip('/')}/{name}-{self.pk}{extension.lower()}"

  class Meta:
    abstract = True

class PhotoClass(File):
  file = ImageField(
    upload_to="tmp/",
    formats={
      "thumb": ["default", ("thumbnail", (300, 200))],
      "desktop": ["default", ("thumbnail", (660, 999))],
    },
    auto_add_fields=True,)

  def published_name(self, format_name, file_name=None):
    stem, _ = os.path.splitext(file_name or self.file.name)
    return f"{stem}.{format_name}.png"
  
  def publish_formats(self):
    storage = self.file.storage
    
    for format_name in self.file.field.formats:
      generated = self.file.process(format_name)
      if not generated:
        raise RuntimeError(f"Could not generate {format_name}")
    
      # The generated image may be PNG; make real JPEG bytes for .jpg.
      with storage.open(generated, "rb") as source:
        with Image.open(source) as image:
          output = BytesIO()
          image.convert("RGBA").save(output, format="PNG", optimize=True)
          
      target = self.published_name(format_name)
      if storage.exists(target):
        storage.delete(target)
    
      saved = storage.save(target, ContentFile(output.getvalue()))
      if saved != target:
        storage.delete(saved)
        raise RuntimeError(f"Storage did not save at {target}")
  
  @property
  def thumb_url(self):
    return self.file.storage.url(self.published_name("thumb")) if self.file else ""
  @property
  def desktop_url(self):
    return self.file.storage.url(self.published_name("desktop")) if self.file else ""
  
  def rename_file(self, folder="misc", new_name=None):
    if not self.pk or not self.file or not self.file.name:
      return
    
    old_file = self.file
    old_name = old_file.name
    target = self.generate_file_slug(folder=folder, name=new_name)
    storage = old_file.storage
    
    if old_name == target:
      # Also backfills or overwrites public variants for an existing image.
      self.publish_formats()
      type(self).objects.filter(pk=self.pk).update(processed=True)
      self.processed = True
      return
    
    # Keep the old original until the replacement has been saved.
    if storage.exists(target):
      storage.delete(target)
    
    with storage.open(old_name, "rb") as source:
      saved_name = storage.save(target, source)
    
    if saved_name != target:
      storage.delete(saved_name)
      raise RuntimeError(f"Storage did not save at {target}")
    
    self.file = saved_name
    
    try:
      self.publish_formats()
      # Do this once, after BOTH public JPEGs have been written.
      type(self).objects.filter(pk=self.pk).update(
        file=saved_name,
        processed=True,)
    except Exception:
      for format_name in self.file.field.formats:
        storage.delete(self.published_name(format_name, saved_name))
      self.file.delete(save=False)  # New original and generated variants.
      self.file = old_name
      raise
    
    self.processed = True
    
    try:
      for format_name in old_file.field.formats:
        old_public = self.published_name(format_name, old_name)
    
        if old_public != self.published_name(format_name, saved_name):
          storage.delete(old_public)
    
      old_file.delete(save=False)  # Old original and generated variants.
    finally:
      # FieldFile.delete() clears the field on this Python object.
      self.file = saved_name
  
  def delete(self, *args, **kwargs):
    print(f'deleting file when photo row is deleted')
    from django.core.files.storage import default_storage
    path = self.file.path
    print(f'delete path: {path}')
    default_storage.delete(path)
    print(f'file deleted')
    print(f'continue to deleting row')
    super().delete(*args, **kwargs)

  def __str__(self):
    return self.file.name or f"Photo {self.pk}"

  class Meta:
    abstract = True

class Flyer(PhotoClass):
  meetup = models.OneToOneField(
    "upcoming.Meetup",
    on_delete=models.CASCADE,
    related_name="flyer",
    null=True, blank=True)

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    print(f'date: {self.meetup.date}')
    new_name = f'{self.meetup.date}_{slugify(self.meetup.title)}'
    self.rename_file(folder="flyers", new_name=new_name)


class LocationLogo(PhotoClass):
  location = models.OneToOneField(
    "upcoming.Location",
    on_delete=models.CASCADE,
    related_name="location_logo",
    null=True, blank=True)

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

    new_name = slugify(self.location.name)
    new_name += f'_{slugify(self.location.city)}'
    
    self.rename_file(folder="location-logos", new_name=new_name)

class LocationRoute(PhotoClass):
  location = models.OneToOneField(
  "upcoming.Location",
  on_delete=models.CASCADE,
  related_name="location_route",
  null=True, blank=True)
 
  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

    new_name = slugify(self.location.name)
    new_name += f'_{slugify(self.location.city)}'
    self.rename_file(folder="location-routes", new_name=new_name)

class Album(models.Model):
  album_id = models.AutoField(primary_key=True)
  title = models.CharField(max_length=100, blank=True, default="")

class Photo(PhotoClass):
  title = models.CharField(max_length=100, blank=True, default="")
  album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)

class Document(File):
  file = models.FileField(upload_to="media/")