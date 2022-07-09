from django.db import models

# Create your models here.
class UserInformation(models.Model):
    fname = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    mobile = models.CharField(max_length=10)
    email = models.EmailField()