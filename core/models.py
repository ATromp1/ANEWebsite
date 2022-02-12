import requests
from allauth.socialaccount.models import SocialAccount, SocialToken
from allauth.account.signals import user_logged_in
from django.contrib.auth.models import User

from django.db import models
from django.dispatch import receiver


class Rank(models.IntegerChoices):
    GM = 0, 'GM'
    OFFICER = 1, "Officer"
    OFFICER_ALT = 2, "Officer Alt"
    RAIDER = 3, "Raider"
    SECOND_MAIN = 4, 'Second Main'
    TRIAL = 5, "Trial"


class Roster(models.Model):
    name = models.CharField(max_length=20, unique=True)
    rank = models.IntegerField(choices=Rank.choices)
    character_id = models.IntegerField(unique=True)
    account_id = models.IntegerField(null=True, blank=True)
    playable_class = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


class Boss(models.Model):
    boss_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.boss_name


class RaidEvent(models.Model):
    name = models.CharField(max_length=30, default='Raid')
    date = models.DateField(unique=True)
    roster = models.ManyToManyField(Roster, blank=True, default=True, related_name='roster')
    bosses = models.ManyToManyField(Boss, through='BossPerEvent')
    late_users = models.ManyToManyField(SocialAccount, blank=True, related_name='late_users')

    def __str__(self):
        return str(self.date)

    def add_late_user(self, current_user_account_id):
        self.late_users.add(SocialAccount.objects.get(uid=current_user_account_id))

    def rem_late_user(self, current_user_account_id):
        self.late_users.remove(SocialAccount.objects.get(uid=current_user_account_id))

    def populate_roster(self):
        for character in Roster.objects.all():
            self.roster.add(Roster.objects.get(name=character))

    def remove_char_from_roster(self, current_user_id):
        current_user_characters = Roster.objects.filter(account_id=current_user_id)
        for item in current_user_characters:
            self.roster.remove(Roster.objects.get(name=item.name))
            self.save()

    def attend_raid(self, current_user_id):
        current_user_characters = Roster.objects.filter(account_id=current_user_id)
        for item in current_user_characters:
            self.roster.add(Roster.objects.get(name=item.name))
            self.save()


class BossPerEvent(models.Model):
    boss = models.ForeignKey(Boss, on_delete=models.CASCADE, null=True)
    raid_event = models.ForeignKey(RaidEvent, on_delete=models.CASCADE, null=True)
    tank = models.ManyToManyField(Roster, blank=True, related_name='rel_tank')
    healer = models.ManyToManyField(Roster, blank=True, related_name='rel_healer')
    mdps = models.ManyToManyField(Roster, blank=True, related_name='rel_mdps')
    rdps = models.ManyToManyField(Roster, blank=True, related_name='rel_rdps')

    def __str__(self):
        return str(self.raid_event.date)

    def dateDisplay(self):
        return str(self.raid_event.date)

    def bossDisplay(self):
        return str(self.boss.boss_name)

    def ajax_to_tank(self, name):
        self.tank.add(Roster.objects.get(name=name))

    def ajax_to_healer(self, name):
        self.healer.add(Roster.objects.get(name=name))

    def ajax_to_mdps(self, name):
        self.mdps.add(Roster.objects.get(name=name))

    def ajax_to_rdps(self, name):
        self.rdps.add(Roster.objects.get(name=name))

    def remove_from_tank(self, name):
        self.tank.remove(Roster.objects.get(name=name))

    def remove_from_healer(self, name):
        self.healer.remove(Roster.objects.get(name=name))

    def remove_from_rdps(self, name):
        self.rdps.remove(Roster.objects.get(name=name))

    def remove_from_mdps(self, name):
        self.mdps.remove(Roster.objects.get(name=name))


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    """
    If new user logs in via battlenet, their characters will be fetched by API and
    their class and account_id will be linked in Roster.
    """
    if not user.is_superuser:
        all_user_characters = get_user_profile_data(request)
        set_account_id_and_class(all_user_characters)


def set_account_id_and_class(char_json):
    """
    Updates the account id and playable class in the Roster with the data received from the API after someone logs in
    """
    for i in range(len(char_json['wow_accounts'])):
        for j in range(len(char_json['wow_accounts'][i]['characters'])):
            account_id = char_json['id']
            char_name = char_json['wow_accounts'][i]['characters'][j]['name']
            playable_class = char_json['wow_accounts'][i]['characters'][j]['playable_class']['name']
            char_id = char_json['wow_accounts'][i]['characters'][j]['id']
            if Roster.objects.filter(name=char_name).exists():
                res = Roster.objects.get(character_id=char_id)
                res.account_id = account_id
                res.playable_class = playable_class
                res.save()


def get_user_profile_data(request):
    """
    API calls to the blizzard endpoint that returns all
    characters that belong to the logged-in user
    """
    current_user = SocialAccount.objects.get(user=request.user)
    access_token = SocialToken.objects.get(account=current_user)
    header = {
        'Authorization': 'Bearer %s' % access_token,
    }
    response = requests.get('https://eu.api.blizzard.com/profile/user/wow?namespace=profile-eu&locale=en_US',
                            headers=header)

    result = response.json()
    return result


def populate_roster_db(api_roster):
    """
    Adding characters from the API call that contains all guild roster characters and filters them by rank
    Also updating the ranks in the CurrentUser database
    """
    raider_ranks = [0, 1, 3, 4, 5]
    for member in api_roster['members']:
        rank = member['rank']
        name = member['character']['name']
        character_id = member['character']['id']
        if rank in raider_ranks:
            Roster.objects.filter(name=name).update_or_create(name=name,
                                                              rank=rank,
                                                              character_id=character_id)


def get_guild_roster(request):
    """
    API calls to the blizzard endpoint that returns all
    characters that exist in A Necessary Evil
"""
    current_user = SocialAccount.objects.filter(user=request.user).first()
    access_token = SocialToken.objects.filter(account=current_user).first()
    header = {
        'Authorization': 'Bearer %s' % access_token,
    }
    response = requests.get(
        'https://eu.api.blizzard.com/data/wow/guild/tarren-mill/a-necessary-evil/roster?namespace=profile-eu&locale=en_US',
        headers=header)
    result = response.json()
    return result
