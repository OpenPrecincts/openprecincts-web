# Generated by Django 2.2.4 on 2019-09-23 21:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_state_show_crowdsourcing_tools'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatewideElection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('election_name', models.CharField(default='', max_length=100)),
                ('dem_name', models.CharField(default='Democrat', max_length=50)),
                ('rep_name', models.CharField(default='Republican', max_length=50)),
                ('dem_property', models.CharField(default='', max_length=20)),
                ('rep_property', models.CharField(default='', max_length=20)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='elections', to='core.State')),
            ],
        ),
    ]