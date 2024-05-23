from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    distance = models.FloatField(null=True, blank=True)  # Optional: store the distance from a reference point

    def __str__(self):
        return self.name
