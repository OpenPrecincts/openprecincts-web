# Generated by Django 2.2.1 on 2019-05-21 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("accounts", "0002_auto_20190521_1843")]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="contact_me",
            field=models.BooleanField(default=False),
        )
    ]
