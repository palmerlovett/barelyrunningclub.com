from django.db import models

class Meetup(models.Model):
  meetup_id = models.AutoField(primary_key=True)
  title = models.CharField(max_length=200)
  date = models.DateField()
  content = models.TextField(blank=True)

  def __str__(self):
    return f'{self.date}, {self.title}'