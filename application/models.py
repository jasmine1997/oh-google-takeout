from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class User(AbstractBaseUser):
    id = models.CharField(max_length=16, primary_key=True)
    access_token = models.CharField(max_length=256)
    refresh_token = models.CharField(max_length=256)
    expiration_time = models.DateTimeField()
