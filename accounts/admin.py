from django.contrib import admin
from .models import UserProfile


class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = (
        "user",
        "state",
        "slack",
    )
    list_display = ("user", "state", "about", "slack")


admin.site.register(UserProfile, ProfileAdmin)
