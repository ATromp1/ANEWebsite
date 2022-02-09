import requests
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db import models, IntegrityError
from django.dispatch import receiver


class Rank(models.IntegerChoices):
    GM = 0, 'GM'
    OFFICER = 1, "Officer"
    OFFICER_ALT = 2, "Officer Alt"
    RAIDER = 3, "Raider"
    SECOND_MAIN = 4, 'Second Main'
    TRIAL = 5, "Trial"


class CurrentUser(models.Model):
    account_id = models.IntegerField()
    character_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=20)
    playable_class = models.CharField(max_length=30, null=True, blank=True)
    rank = models.IntegerField(choices=Rank.choices, null=True)

    def __str__(self):
        return self.name


class Roster(models.Model):
    name = models.CharField(max_length=20, unique=True)
    rank = models.IntegerField(choices=Rank.choices)
    character_id = models.IntegerField(unique=True)
    playable_class = models.CharField(max_length=50, null=True, blank=True)
    # role = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class Boss(models.Model):
    boss_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.boss_name


class RaidEvent(models.Model):
    name = models.CharField(max_length=30, default='Raid')
    date = models.DateField(unique=True)
    roster = models.ManyToManyField(Roster, blank=True, default=True)
    bosses = models.ManyToManyField(Boss, through='BossPerEvent')

    def __str__(self):
        return str(self.date)

    def populate_roster(self):
        for character in Roster.objects.all():
            self.roster.add(Roster.objects.get(name=character))

    def remove_char_from_roster(self, current_user_id):
        user_chars_in_roster = get_chars_in_roster(current_user_id)
        for item in user_chars_in_roster:
            self.roster.remove(Roster.objects.get(name=item))
            self.save()

    def sign_in(self, current_user_id):
        user_chars_in_roster = get_chars_in_roster(current_user_id)
        for item in user_chars_in_roster:
            self.roster.add(Roster.objects.get(name=item))
            self.save()


class BossPerEvent(models.Model):
    boss = models.ForeignKey(Boss, on_delete=models.CASCADE, null=True)
    raid_event = models.ForeignKey(RaidEvent, on_delete=models.CASCADE, null=True)
    # inherited_roster = models.ManyToManyField(Roster, blank=True)
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


def get_chars_in_roster(current_user_id):
    """
    Cross-referencing characters that exist in both de Roster database and the CurrentUser database
    :return: a list of characters
    """
    roster = []
    for character in Roster.objects.all():
        roster.append(character.name)
    user_chars = []
    for character in CurrentUser.objects.filter(account_id=current_user_id):
        user_chars.append(character.name)
    user_chars_in_roster = set(roster).intersection(set(user_chars))
    return user_chars_in_roster


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    """
    If new user logs in via battlenet, their characters will be fetched by API and
    stored in CurrentUser.
    """
    account_id = SocialAccount.objects.get(user=request.user).extra_data['id']
    if not CurrentUser.objects.filter(account_id=account_id).exists():
        api_profiles = get_profile_summary(request)
        populate_char_db(api_profiles)


def populate_char_db(char_json):
    """
    Updates the current user's characters filtered by realm = tarrenmill and level = 60
    """
    for i in range(len(char_json['wow_accounts'])):
        for j in range(len(char_json['wow_accounts'][i]['characters'])):
            realm_id = char_json['wow_accounts'][i]['characters'][j]['realm']['id']
            character_level = char_json['wow_accounts'][i]['characters'][j]['level']
            if realm_id == 1306 and character_level == 60:
                account_id = char_json['id']
                char_name = char_json['wow_accounts'][i]['characters'][j]['name']
                char_id = char_json['wow_accounts'][i]['characters'][j]['id']
                playable_class = char_json['wow_accounts'][i]['characters'][j]['playable_class']['name']
                try:
                    CurrentUser.objects.update_or_create(name=char_name,
                                                         account_id=account_id,
                                                         character_id=char_id,
                                                         playable_class=playable_class,
                                                         rank='7')
                except IntegrityError:
                    pass


def get_profile_summary(request):
    """
    API calls to the blizzard endpoint that returns all
    characters that belong to the logged-in user
    """
    current_user = SocialAccount.objects.filter(user=request.user).first()
    access_token = SocialToken.objects.filter(account=current_user).first()
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
        CurrentUser.objects.filter(name=name).update(rank=rank)
        if rank in raider_ranks:
            Roster.objects.filter(name=name).update_or_create(name=name,
                                                              rank=rank,
                                                              character_id=character_id)


def update_guild_roster_classes():
    """
    Pulls class data from Current user and cross-references it to characters in Roster to fill/update their respective
    character classes
    """
    for character in Roster.objects.all():
        if CurrentUser.objects.filter(character_id=character.character_id).exists():
            playable_class = CurrentUser.objects.get(
                character_id=character.character_id).playable_class
            Roster.objects.filter(character_id=character.character_id).update(
                playable_class=playable_class)


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
