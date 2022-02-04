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


class RaidInstance(models.Model):
    boss = models.CharField(max_length=20)
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class RaidEvent(models.Model):
    name = models.CharField(max_length=30, default='Raid')
    date = models.DateField()
    roster = models.ManyToManyField(Roster, blank=True, default=True)
    sign_off = models.ManyToManyField(CurrentUser, blank=True)

    def __str__(self):
        return self.name

    def event_roster(self):
        roster = []
        for character in Roster.objects.all():
            roster.append(character.name)
        user_chars = []
        for character in CurrentUser.objects.all():
            user_chars.append(character.name)
        diff = set(roster).difference(set(user_chars))
        for item in diff:
            self.roster.add(Roster.objects.get(name=item))

        return diff

    def event_sign_offs(self):
        roster = []
        for character in Roster.objects.all():
            roster.append(character.name)
        user_chars = []
        for character in CurrentUser.objects.all():
            user_chars.append(character.name)
        intersection = set(roster).intersection(set(user_chars))
        return intersection