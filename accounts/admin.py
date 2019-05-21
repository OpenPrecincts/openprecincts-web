from django.contrib import admin
from .models import UserProfile


class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ("user", "state", "slack", "contact_me")
    list_display = ("user", "state", "about", "slack", "contact_me")


admin.site.register(UserProfile, ProfileAdmin)
