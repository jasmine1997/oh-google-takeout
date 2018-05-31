from django.db import models


class Member(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    access_token = models.CharField(max_length=256)
    refresh_token = models.CharField(max_length=256)
    expiration_time = models.DateTimeField()
