# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-05 09:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0007_auto_20161222_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='mail_to',
            field=models.CharField(default='', max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskcondition',
            name='margin',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
