from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    state = models.CharField(max_length=2)
    about = models.TextField(blank=True)
    slack = models.BooleanField(default=False)
    contact_me = models.BooleanField(default=False)
    private_notes = models.TextField(blank=True)
