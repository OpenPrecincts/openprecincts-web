from django.contrib import admin
from .models import Official, ContactLog, EmailMessage


class OfficialAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("locality", "title", "first_name", "last_name")}),
        ("Contact Details", {"fields": ("phone_number", "email")}),
        ("Additional Info", {"fields": ("job_title", "notes")}),
        (
            "Administrative",
            {"fields": ("active", "created_at", "created_by", "updated_at")},
        ),
    )

    readonly_fields = ("created_at", "updated_at", "created_by")
    list_display = ("name", "job_title", "locality", "active")
    list_filter = ("locality__state",)

    def name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Official, OfficialAdmin)


class ContactAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("official", "contact_date", "contacted_by", "notes")}),
        ("Administrative", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("contact_date", "official_contacted", "contacted_by")
    list_filter = ("official__locality__state",)
    date_hierarchy = "contact_date"

    def official_contacted(self, obj):
        return f"{obj.official} ({obj.official.locality})"


admin.site.register(ContactLog, ContactAdmin)


class EmailMessageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("subject_template", "body_template", "officials")}),
        (
            "Administrative",
            {"fields": ("sent_at", "created_at", "updated_at", "created_by")},
        ),
    )

    list_display = ("subject_template", "sent_at", "created_by")
    date_hierarchy = "created_at"


admin.site.register(EmailMessage, EmailMessageAdmin)
