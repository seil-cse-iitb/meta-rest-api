# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-10 09:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0009_auto_20170105_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskcondition',
            name='string_value',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='database',
            name='type',
            field=models.CharField(choices=[('Q', 'MQTT'), ('G', 'MongoDB'), ('S', 'MySQL'), ('U', 'UDP Proxy')], max_length=1),
        ),
        migrations.AlterField(
            model_name='datafield',
            name='field_type',
            field=models.CharField(choices=[('I', 'Integer'), ('F', 'Float'), ('S', 'String')], max_length=1),
        ),
    ]
