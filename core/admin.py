from django.contrib import admin
from .models import Locality

class LocalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'official_url')
    list_filter = ('state',)

admin.site.register(Locality, LocalityAdmin)
