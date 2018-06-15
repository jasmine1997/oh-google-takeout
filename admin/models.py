from django.db import models
from django.contrib.auth.models import User
# from django.contrib.postgres.fields import ArrayField


class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='admin')


# class FileMetadata(models.Model):
#     name = models.CharField(max_length=256)
#     description = models.TextField()
#     tags = ArrayField(models.CharField(max_length=32))
