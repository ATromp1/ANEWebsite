# Generated by Django 4.0.2 on 2022-02-03 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0024_remove_raidevent_sign_off_raidevent_sign_off'),
    ]

    operations = [
        migrations.AddField(
            model_name='raidevent',
            name='roster',
            field=models.ManyToManyField(blank=True, null=True, to='players.Roster'),
        ),
    ]
