# Generated by Django 2.2.1 on 2019-05-21 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("accounts", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="userprofile", name="about", field=models.TextField(blank=True)
        ),
        migrations.AddField(
            model_name="userprofile",
            name="private_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="slack",
            field=models.BooleanField(default=False),
        ),
    ]
