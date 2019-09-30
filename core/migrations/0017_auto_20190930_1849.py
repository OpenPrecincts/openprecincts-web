# Generated by Django 2.2.4 on 2019-09-30 18:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0016_auto_20190924_1757'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrecinctNameMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('election_precinct_name', models.CharField(max_length=100)),
                ('shapefile_precinct_name', models.CharField(blank=True, default='', max_length=100)),
                ('notes', models.TextField(default='')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('matched_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='names_matched', to=settings.AUTH_USER_MODEL)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='precinct_names', to='core.State')),
            ],
        ),
        migrations.DeleteModel(
            name='StateCycle',
        ),
    ]
