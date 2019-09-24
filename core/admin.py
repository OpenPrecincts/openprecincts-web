from django.contrib import admin
from .models import State, Locality, StateCycle, ElectionResult, StatewideElection


class CycleAdmin(admin.TabularInline):
    model = StateCycle


class StatewideElectionInline(admin.TabularInline):
    model = StatewideElection


class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "status")
    readonly_fields = ("name", "abbreviation", "census_geoid")
    inlines = [CycleAdmin, StatewideElectionInline]


admin.site.register(State, StateAdmin)


class LocalityAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "official_url")
    list_filter = ("state",)

    readonly_fields = ("state",)


admin.site.register(Locality, LocalityAdmin)


class ElectionResultInline(admin.TabularInline):
    model = ElectionResult


class StatewideElectionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "state", "year", "is_general", "office_type")
    list_filter = ("state", "year", "is_general", "office_type")
    inlines = [ElectionResultInline]


admin.site.register(StatewideElection, StatewideElectionAdmin)
