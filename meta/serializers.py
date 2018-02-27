from rest_framework import serializers
from .models import Database, SensorChannel ,Sensor ,SensorType, DataField, SensorDatabase

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ('sensor_id','channel','sensor_name','public_name','location','mac_id','database','start_date')

class DatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Database
        fields = ('database_id','database_name','schema','type','ip','port','user_id','password')

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataField
        fields = ('field_number','field_name','field_type')

class SensorDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorDatabase
        fields = ('sensor','purpose','database')

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorChannel
        fields = ('id','sensor_type','display_name','channel')
