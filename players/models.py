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
    sign_off = models.ManyToManyField(CurrentUser, blank=True)

    def __str__(self):
        return self.name

    def roster(self):
        dummy = []
        signed_off = CurrentUser.objects.all()
        all_characters = Roster.objects.all()
        # roster = all_characters.difference(signed_off)
        # print(roster)
        return dummy



    def create_event(self):
        pass

    def delete_event(self):
        pass

    def edit_event(self):
        pass
