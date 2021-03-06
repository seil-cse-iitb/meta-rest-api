# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-19 11:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('operation_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SensorTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_date', models.DateField()),
                ('status', models.CharField(choices=[('R', 'Running'), ('P', 'Pending'), ('F', 'Finished'), ('E', 'Error')], max_length=1)),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meta.Sensor')),
            ],
        ),
        migrations.CreateModel(
            name='SensorTaskLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_date', models.DateField()),
                ('status', models.CharField(choices=[('R', 'Running'), ('P', 'Pending'), ('F', 'Finished'), ('E', 'Error')], max_length=1)),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meta.Sensor')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('task_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('frequency', models.CharField(choices=[('E', 'Event Based'), ('D', 'Daily'), ('H', 'Hourly')], max_length=1)),
                ('next_run', models.DateField()),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meta.SensorChannel')),
                ('data_source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meta.Database')),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meta.Operation')),
            ],
        ),
        migrations.CreateModel(
            name='TaskCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condition', models.CharField(choices=[('=', '=='), ('!', '!='), ('<', '<'), ('L', '<='), ('>', '>'), ('G', '>='), ('C', 'Count'), ('I', 'Increment By')], max_length=1)),
                ('value', models.IntegerField()),
                ('Field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meta.DataField')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meta.Task')),
            ],
        ),
        migrations.AddField(
            model_name='sensortasklog',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meta.Task'),
        ),
        migrations.AddField(
            model_name='sensortask',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meta.Task'),
        ),
    ]
