from django.db import models
class Bird(models.Model):
  name = models.CharField(max_length=200, unique=True)
  species = models.CharField(max_length=200, unique=True, default="")

  def __str__(self):
    return self.name
