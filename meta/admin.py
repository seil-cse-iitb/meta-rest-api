from django.contrib import admin

# Register your models here.

from .models import *


@admin.register(DataField)
class DataFieldAdmin(admin.ModelAdmin):
    list_display = ('sensor_type', 'field_number', 'field_name','field_type')
    list_filter = ('sensor_type',)
    search_fields = ['field_name']


@admin.register(Database)
class  DatabaseAdmin(admin.ModelAdmin):
    list_display = ('database_name', 'type', 'ip','port')
    list_filter = ('type',)
    search_fields = ['database_name']


@admin.register(SensorType)
class  SensorTypeAdmin(admin.ModelAdmin):
    list_display = ('sensor_type','sensor_name')
    list_filter = ('sensor_name',)
    search_fields = ['sensor_name']


@admin.register(SensorChannel)
class  SensorChannelAdmin(admin.ModelAdmin):
    list_display = ('sensor_type','channel')
    list_filter = ('sensor_type','channel')
    search_fields = ['channel']


@admin.register(Sensor)
class  SensorAdmin(admin.ModelAdmin):
    list_display = ('sensor_name','sensor_id','channel','location','mac_id')
    list_filter = ('channel','location')
    search_fields = ['sensor_id','sensor_name']


@admin.register(SensorDatabase)
class  SensorAdmin(admin.ModelAdmin):
    list_display = ('sensor','purpose','database')
    list_filter = ('sensor','purpose','database')
    #search_fields = ['sensor','purpose','database']


