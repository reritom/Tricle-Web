# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-23 21:56
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('scrambler', '0023_auto_20170723_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='expiringurl',
            name='user_name',
            field=models.CharField(default=0, max_length=255),
        ),
        migrations.AlterField(
            model_name='expiringurl',
            name='created',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2017, 7, 23, 21, 56, 41, 198974, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_login',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 23, 22, 56, 41, 197974)),
        ),
    ]
