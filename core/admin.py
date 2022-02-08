from django.contrib import admin
from .models import CurrentUser, Roster, RaidEvent, RaidInstance, RaidBosses, Boss


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_id', 'account_id', 'playable_class', 'rank']



class RosterAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_id', 'playable_class', 'rank']


class RaidEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']


class RaidInstanceAdmin(admin.ModelAdmin):
    filter_horizontal = ('bosses',)



admin.site.register(Boss)
admin.site.register(CurrentUser, PlayerAdmin)
admin.site.register(Roster, RosterAdmin)
admin.site.register(RaidEvent, RaidEventAdmin)
admin.site.register(RaidBosses)
admin.site.register(RaidInstance, RaidInstanceAdmin)
