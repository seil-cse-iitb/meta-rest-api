from __future__ import unicode_literals

from django.db import models

# Create your models here.
# Create your models here.
class Database(models.Model):
    database_id = models.CharField(max_length=20, primary_key=True)

    SOURCE_TYPES = (
        ('Q', 'MQTT'),
        ('G', 'MongoDB'),
        ('S', 'MySQL'),
    )
    database_name = models.CharField(max_length=50)
    schema = models.CharField(max_length=50)
    type = models.CharField(max_length=1, choices=SOURCE_TYPES)
    ip = models.CharField(max_length=15)
    port = models.IntegerField()
    user_id = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.database_name

class SensorType(models.Model):
    sensor_type = models.CharField(max_length=10,primary_key=True)
    sensor_name = models.CharField(max_length=50)

    def __str__(self):
        return self.sensor_name


class SensorChannel(models.Model):
    CHANNEL_TYPES = (
        ('data', 'Data'),
        ('H', 'Hartbeat'),
        ('info', 'Sensor information'),
    )
    sensor_type = models.ForeignKey(SensorType)
    channel = models.CharField(max_length=5, choices=CHANNEL_TYPES)

    def __str__(self):
        return str(self.sensor_type) + ' : ' + str(self.channel)
    class Meta:
        unique_together = ('sensor_type', 'channel')

class DataField(models.Model):
    FIELD_TYPES =(
        ('I','Integer'),
        ('F', 'Float'),
    )
    sensor_type = models.ForeignKey(SensorChannel)
    field_number = models.IntegerField()
    field_name = models.CharField(max_length=50)
    field_type = models.CharField(max_length=1, choices=FIELD_TYPES)

    def __str__(self):
        return '(' + str(self.sensor_type) + ')    ' + str(self.field_number) + ' : ' + str(self.field_name)

    class Meta:
        unique_together = ('sensor_type', 'field_number')

class Sensor(models.Model):
    sensor_id = models.CharField(max_length=20,primary_key=True)
    channel = models.ForeignKey(SensorChannel)
    sensor_name = models.CharField(max_length=50)
    #sensor_type = models.ForeignKey(SensorType)
    location = models.CharField(max_length=50)
    mac_id = models.CharField(max_length=50)
    database = models.ForeignKey(Database)
    start_date = models.DateField()

    def __str__(self):
        return self.sensor_name + ' (' + str(self.start_date) + ' )'

    class Meta:
        unique_together = ('sensor_id', 'start_date')

class SensorDatabase(models.Model):
    DATABASE_PURPOSE = (
        ('P', 'Primary Storage'),
        ('B', 'Primary Broker'),
        ('L', 'Local Broker'),
    )
    sensor = models.ForeignKey(Sensor)
    purpose = models.CharField(max_length=1, choices=DATABASE_PURPOSE)
    database = models.ForeignKey(Database)

    def __str__(self):
        return str(self.sensor) + ":" +  str(self.database)

    class Meta:
        unique_together = ('sensor', 'purpose','database')

