# Generated by Django 4.0.1 on 2022-01-31 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='character_id',
            field=models.IntegerField(unique=True),
        ),
    ]