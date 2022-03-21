
from django.contrib.gis import forms
from django.contrib.gis.db import models
# Create your models here.

class Bank(models.Model):
    name = models.CharField(max_length=20)
    poly = models.PolygonField()

    def __str__(self):
        return self.name
