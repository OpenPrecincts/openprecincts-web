from django.contrib import admin
from .models import File, Transformation


class FileAdmin(admin.ModelAdmin):
    readonly_fields = (
        "stage",
        "mime_type",
        "size",
        "s3_path",
        "source_filename",
        "from_transformation",
        "locality",
        "cycle",
        "created_by",
    )
    list_display = ("source_filename", "stage", "locality", "active")
    list_filter = ("mime_type", "locality__state")


admin.site.register(File, FileAdmin)


class TransformationAdmin(admin.ModelAdmin):
    readonly_fields = (
        "transformation",
        "input_files",
        "error",
        "created_at",
        "created_by",
        "finished_at",
    )

    list_display = ("transformation", "cycle", "created_at", "finished_at")


admin.site.register(Transformation, TransformationAdmin)
