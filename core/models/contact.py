from django.db import models
from django.contrib.auth.models import User
from core.models import Locality


class Official(models.Model):
    locality = models.ForeignKey(Locality, on_delete=models.PROTECT,
                                 related_name="officials")
    # keeping this separate for mail merge
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=10, choices=(
        ('Ms.', 'Ms.'),
        ('Mr.', 'Mr.'),
        ('Dr.', 'Dr.'),
        ('Hon.', 'Hon.'),
        ('', '-none-'),
    ))
    # keeping this as simple as possible
    # we won't worry about multiple poc for a person
    phone_number = models.CharField(max_length=10, blank=True)
    email = models.EmailField(blank=True)
    job_title = models.CharField(max_length=300, blank=True)
    notes = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    # change tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT,
                                   related_name="created_officials")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ContactLog(models.Model):
    official = models.ForeignKey(Official, on_delete=models.PROTECT,
                                 related_name="contact_log_entries")
    contact_date = models.DateField()
    contacted_by = models.ForeignKey(User,
                                     on_delete=models.PROTECT,
                                     related_name="contact_log_entries")
    notes = models.TextField(blank=True)

    # change tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
