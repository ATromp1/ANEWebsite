# Generated by Django 4.0.1 on 2022-01-31 18:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_roster_name'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Player',
            new_name='CurrentUser',
        ),
    ]