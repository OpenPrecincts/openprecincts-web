# Generated by Django 2.1.7 on 2019-02-15 02:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('stage', models.CharField(choices=[('S', 'Source'), ('I', 'Intermediate'), ('F', 'Final')], max_length=1)),
                ('mime_type', models.CharField(max_length=100)),
                ('size', models.PositiveIntegerField()),
                ('s3_path', models.CharField(editable=False, max_length=500)),
                ('source_filename', models.CharField(blank=True, max_length=300)),
                ('notes', models.TextField(blank=True)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_files', to=settings.AUTH_USER_MODEL)),
                ('locality', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='files', to='core.Locality')),
                ('official', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='files', to='contact.Official')),
                ('parent_file', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='files.File')),
            ],
        ),
    ]
