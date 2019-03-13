from django.contrib import admin
from .models import File


class FileAdmin(admin.ModelAdmin):
    readonly_fields = (
        "stage",
        "mime_type",
        "size",
        "s3_path",
        "source_filename",
        "locality",
        "parent_file",
        "created_by",
    )
    list_display = ("source_filename", "stage", "locality", "active")
    list_filter = ("mime_type", "locality__state")


admin.site.register(File, FileAdmin)
