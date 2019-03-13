# Generated by Django 2.1.7 on 2019-03-04 21:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0003_auto_20190219_0042"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ContactLog",
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
                ("contact_date", models.DateField()),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "contacted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="contact_log_entries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Official",
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
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                (
                    "title",
                    models.CharField(
                        choices=[
                            ("Ms.", "Ms."),
                            ("Mr.", "Mr."),
                            ("Dr.", "Dr."),
                            ("Hon.", "Hon."),
                            ("", "-none-"),
                        ],
                        max_length=10,
                    ),
                ),
                ("phone_number", models.CharField(blank=True, max_length=10)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("job_title", models.CharField(blank=True, max_length=300)),
                ("notes", models.TextField(blank=True)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_officials",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "locality",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="officials",
                        to="core.Locality",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="contactlog",
            name="official",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="contact_log_entries",
                to="contact.Official",
            ),
        ),
    ]
