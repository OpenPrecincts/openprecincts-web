from django.contrib import admin
from .models import File, Transformation


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
        "from_transformation",
        "locality",
        "created_by",
    )
    list_display = ("filename", "stage", "cycle", "active")
    list_filter = ("stage", "mime_type", "locality__state")
    actions = [make_active, make_inactive, make_final]


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
