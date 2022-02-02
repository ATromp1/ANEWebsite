# Generated by Django 4.0.2 on 2022-02-01 14:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0012_alter_currentuser_rank_alter_roster_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='roster',
            name='character_id',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='RaidEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('roster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='players.roster')),
                ('sign_off', models.ManyToManyField(to='players.CurrentUser')),
            ],
        ),
    ]