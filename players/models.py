from django.db import models


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
    rank = models.IntegerField(choices=Rank.choices, null=True)

    def __str__(self):
        return self.name


class Roster(models.Model):
    name = models.CharField(max_length=20, unique=True)
    rank = models.IntegerField(choices=Rank.choices)
    character_id = models.IntegerField(unique=True)
    in_raid = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class RaidBosses(models.Model):
    boss_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.boss_name

class RaidInstance(models.Model):
    name = models.CharField(max_length=40, null=True)
    bosses = models.ManyToManyField(RaidBosses, blank=True)

    def __str__(self):
        return self.name


class RaidEvent(models.Model):
    name = models.CharField(max_length=30, default='Raid')
    date = models.DateField(unique=True)
    roster = models.ManyToManyField(Roster, blank=True, default=True)

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


def get_chars_in_roster(current_user_id):
    roster = []
    for character in Roster.objects.all():
        roster.append(character.name)
    user_chars = []
    for character in CurrentUser.objects.filter(account_id=current_user_id):
        user_chars.append(character.name)
    user_chars_in_roster = set(roster).intersection(set(user_chars))
    return user_chars_in_roster
