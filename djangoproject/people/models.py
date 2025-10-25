from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name
