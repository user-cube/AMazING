from django.db import models


# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=200)
    day = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
