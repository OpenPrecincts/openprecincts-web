# Generated by Django 2.2.4 on 2019-09-24 01:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20190924_0141'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statewideelection',
            name='election_name',
        ),
    ]
