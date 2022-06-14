# Generated by Django 4.0.4 on 2022-06-12 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FightingRomm',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('two_players', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='MatchingQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('waiting_users', models.TextField()),
            ],
        ),
    ]