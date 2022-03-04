from django.contrib import admin
from .models import Roster, RaidEvent, BossPerEvent, Boss, LateUser, UserCharacters


class RosterAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_id', 'account_id', 'playable_class', 'rank']


class RaidEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']

class BossAdmin(admin.ModelAdmin):
    list_display = ['boss_name', 'boss_id']

class BossPerEventAdmin(admin.ModelAdmin):
    list_display = ['dateDisplay', 'bossDisplay']
    exclude = ['boss']

class LateUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'minutes_late']

class UserCharactersAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_id', 'account_id', 'playable_class']


admin.site.register(LateUser, LateUserAdmin)
admin.site.register(Boss, BossAdmin)
admin.site.register(Roster, RosterAdmin)
admin.site.register(RaidEvent, RaidEventAdmin)
admin.site.register(BossPerEvent, BossPerEventAdmin)
admin.site.register(UserCharacters, UserCharactersAdmin)
