# Generated by Django 2.2.4 on 2019-09-24 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0013_auto_20190924_0135")]

    operations = [
        migrations.RemoveField(model_name="statewideelection", name="cycle"),
        migrations.AddField(
            model_name="statewideelection",
            name="year",
            field=models.CharField(default=2016, max_length=4),
            preserve_default=False,
        ),
    ]
