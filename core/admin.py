from django.contrib import admin
from .models import State, Locality, StateCycle


class CycleAdmin(admin.TabularInline):
    model = StateCycle


class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "status")
    readonly_fields = ("name", "abbreviation", "census_geoid")
    inlines = [CycleAdmin]


admin.site.register(State, StateAdmin)


class LocalityAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "official_url")
    list_filter = ("state",)

    readonly_fields = ("state",)


admin.site.register(Locality, LocalityAdmin)
