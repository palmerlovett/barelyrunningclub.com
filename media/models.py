from django.db import models

# Create your models here.

class File(models.Model):
  file = models.ImageField(upload_to="tmp/")
  uploaded_at = models.DateTimeField(auto_now_add=True)
  class Meta:
    abstract = True

class Flyer(models.Model):
	file = models.OneToOneField(
    File,
    on_delete=models.CASCADE,
    primary_key=True,)

class Photo(models.Model):
	file = models.OneToOneField(
    File,
    on_delete=models.CASCADE,
    primary_key=True,)

class Document(models.Model):
	event = models.OneToOneField(
    File,
    on_delete=models.CASCADE,
    primary_key=True,)
	file = models.FileField(upload_to="tmp/")