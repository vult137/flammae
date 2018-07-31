from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User as usr

# Create your models here.


class User(AbstractUser):
    AUTH_CHOICES = (
        (1, 'ViewAuth'),
        (2, 'EnableAuth')
    )
    company = models.CharField(max_length=50)
    auth = models.IntegerField(null=False, default=1, choices=AUTH_CHOICES)

    class Meta(AbstractUser.Meta):
        pass
