from django.contrib import admin
from .models import State, Locality, StateCycle, Election, ElectionResult


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


class ElectionResultInline(admin.TabularInline):
    model = ElectionResult


class ElectionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "cycle", "is_general", "office_type")
    list_filter = ("cycle__state", "cycle__year", "office_type")
    readonly_fields = ("cycle", "is_general", "office_type")
    inlines = [ElectionResultInline]


admin.site.register(Election, ElectionAdmin)
