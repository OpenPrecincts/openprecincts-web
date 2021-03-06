# Generated by Django 2.2 on 2019-04-16 21:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("files", "0004_auto_20190411_2115"),
    ]

    operations = [
        migrations.RemoveField(model_name="file", name="parent_file"),
        migrations.CreateModel(
            name="Transformation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transformation",
                    models.PositiveIntegerField(
                        choices=[(1, "ZIP"), (2, "TO_GEOJSON")]
                    ),
                ),
                ("error", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_transformations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "input_files",
                    models.ManyToManyField(
                        related_name="transformations", to="files.File"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="file",
            name="from_transformation",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="outputs",
                to="files.Transformation",
            ),
        ),
    ]
