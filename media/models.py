from django.db import models

# Create your models here.

class File(models.Model):
  file = models.ImageField(upload_to="photos/")
  uploaded_at = models.DateTimeField(auto_now_add=True)
  class Meta:
    abstract = True

class Flyer(File):
  flyer_id = models.AutoField(primary_key=True)
  meetup = models.OneToOneField(
  	"upcoming.Meetup",
  	on_delete=models.CASCADE,
  	related_name="flyer",)

  def save(self, *args, **kwargs):
  	super().save(*args, **kwargs)


class Album(models.Model):
	album_id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=100)


class Photo(File):
  photo_id = models.AutoField(primary_key=True)
  album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)

class Document(File):
	doc_id = models.AutoField(primary_key=True)
	file = models.FileField(upload_to="media/")


