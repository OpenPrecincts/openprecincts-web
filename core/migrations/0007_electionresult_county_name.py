# Generated by Django 2.2.1 on 2019-05-03 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_election_electionresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='electionresult',
            name='county_name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]