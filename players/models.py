from django.db import models

class Player(models.Model):
    account_id = models.IntegerField()
    character_id = models.IntegerField()
    name = models.CharField(max_length=20)

    def import_account_summary(self):
        pass
