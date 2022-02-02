from django.contrib import admin
from .models import CurrentUser, Roster, RaidEvent


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_id', 'account_id', 'rank']


class RosterAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_id', 'rank']

class RaidEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']

admin.site.register(CurrentUser, PlayerAdmin)
admin.site.register(Roster, RosterAdmin)
admin.site.register(RaidEvent, RaidEventAdmin)