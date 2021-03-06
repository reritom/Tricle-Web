# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-23 20:16
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('scrambler', '0019_auto_20170723_2105'),
    ]

    operations = [
        migrations.AddField(
            model_name='expiringurl',
            name='number_of_files',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='expiringurl',
            name='created',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2017, 7, 23, 20, 16, 19, 427948, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_login',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 23, 21, 16, 19, 426447)),
        ),
    ]
