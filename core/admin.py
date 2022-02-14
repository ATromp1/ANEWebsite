from django.contrib import admin
from .models import Roster, RaidEvent, BossPerEvent, Boss, LateUser


class RosterAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_id', 'account_id', 'playable_class', 'rank']


class RaidEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']


class BossPerEventAdmin(admin.ModelAdmin):
    list_display = ['dateDisplay', 'bossDisplay']

class LateUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'minutes_late']


admin.site.register(LateUser, LateUserAdmin)
admin.site.register(Boss)
admin.site.register(Roster, RosterAdmin)
admin.site.register(RaidEvent, RaidEventAdmin)
admin.site.register(BossPerEvent, BossPerEventAdmin)

