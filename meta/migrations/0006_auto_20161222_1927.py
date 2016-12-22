# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-22 13:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0005_task_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='actual',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='expected',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sensortask',
            name='run_date',
            field=models.DateTimeField(),
        ),
    ]
