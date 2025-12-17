from django.db import models
from model_utils.models import TimeStampedModel


class Gathering(TimeStampedModel):
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
