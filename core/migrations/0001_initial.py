# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Distance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dist', models.IntegerField()),
            ],
            options={
                'db_table': 'distance',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('beaconId', models.CharField(max_length=200, serialize=False, primary_key=True)),
                ('registered', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=200, null=True)),
                ('activationTime', models.DateTimeField(null=True)),
                ('lastUpdate', models.DateTimeField()),
            ],
            options={
                'db_table': 'item',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'room',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ipAddress', models.CharField(max_length=200)),
                ('registered', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=200)),
                ('pollingFrequency', models.CharField(max_length=200, null=True)),
                ('lastUpdate', models.DateTimeField()),
                ('room', models.ForeignKey(to='core.Room', null=True)),
            ],
            options={
                'db_table': 'station',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='item',
            name='room',
            field=models.ForeignKey(to='core.Room', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='distance',
            name='item',
            field=models.ForeignKey(to='core.Item'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='distance',
            name='station',
            field=models.ForeignKey(to='core.Station'),
            preserve_default=True,
        ),
    ]
