from django.db import models

class Stage(models.Model):
    # New, Contacted, Converted, Unconverted
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
