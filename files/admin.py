from django.contrib import admin
from .models import File


def make_active(modeladmin, request, queryset):
    queryset.update(active=True)


def make_inactive(modeladmin, request, queryset):
    queryset.update(active=False)


def make_final(modeladmin, request, queryset):
    # don't allow updating source to final
    queryset.filter(stage="I").update(stage="F")


class FileAdmin(admin.ModelAdmin):
    readonly_fields = (
        "stage",
        "mime_type",
        "size",
        "s3_path",
        "filename",
        "locality",
        "created_by",
        "created_at",
    )
    list_display = ("filename", "stage", "created_at", "active")
    list_filter = ("stage", "mime_type", "locality__state")
    actions = [make_active, make_inactive, make_final]


admin.site.register(File, FileAdmin)
