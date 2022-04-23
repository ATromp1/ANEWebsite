from django.contrib import admin
from .models import BossWishes, Roster, RaidEvent, BossPerEvent, Boss, LateUser, UserCharacters, AbsentUser


class RosterAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_id',
                    'account_id', 'playable_class', 'rank']


class RaidEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']


class BossAdmin(admin.ModelAdmin):
    list_display = ['boss_name', 'boss_id', 'boss_wishes_visible']


class BossPerEventAdmin(admin.ModelAdmin):
    list_display = ['dateDisplay', 'bossDisplay', 'published']
    exclude = ['boss']


class LateUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'minutes_late']


class AbsentUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'date']


class UserCharactersAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_id', 'account_id', 'playable_class']


class BossWishesAdmin(admin.ModelAdmin):
    list_display = ['character_id', 'wishes']


admin.site.register(LateUser, LateUserAdmin)
admin.site.register(AbsentUser, AbsentUserAdmin)
admin.site.register(Boss, BossAdmin)
admin.site.register(Roster, RosterAdmin)
admin.site.register(RaidEvent, RaidEventAdmin)
admin.site.register(BossPerEvent, BossPerEventAdmin)
admin.site.register(UserCharacters, UserCharactersAdmin)
admin.site.register(BossWishes, BossWishesAdmin)
