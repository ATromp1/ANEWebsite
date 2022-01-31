from django.contrib import admin
from .models import CurrentUser, Roster


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_id', 'account_id', 'rank']


class RosterAdmin(admin.ModelAdmin):
    list_display = ['name', 'rank']


admin.site.register(CurrentUser, PlayerAdmin)
admin.site.register(Roster, RosterAdmin)
