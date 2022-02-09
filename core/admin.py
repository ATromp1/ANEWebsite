from django.contrib import admin
from .models import CurrentUser, Roster, RaidEvent, BossPerEvent, Boss


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_id', 'account_id', 'playable_class', 'rank']


class RosterAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_id', 'playable_class', 'rank']


class RaidEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']

class BossPerEventAdmin(admin.ModelAdmin):
    list_display = ['dateDisplay', 'bossDisplay']

admin.site.register(Boss)
admin.site.register(CurrentUser, PlayerAdmin)
admin.site.register(Roster, RosterAdmin)
admin.site.register(RaidEvent, RaidEventAdmin)
admin.site.register(BossPerEvent, BossPerEventAdmin)
