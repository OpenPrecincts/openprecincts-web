# Generated by Django 2.2.4 on 2019-09-24 17:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0010_file_from_transformation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='cycle',
        ),
    ]