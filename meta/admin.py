from django.contrib import admin

# Register your models here.

from .models import *


@admin.register(DataField)
class DataFieldAdmin(admin.ModelAdmin):
    list_display = ('sensor_type', 'field_number', 'field_name', 'field_type')
    list_filter = ('sensor_type',)
    search_fields = ['field_name']


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    list_display = ('database_name', 'type', 'ip', 'port')
    list_filter = ('type',)
    search_fields = ['database_name']


@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ('sensor_type', 'sensor_name')
    list_filter = ('sensor_name',)
    search_fields = ['sensor_name']


@admin.register(SensorChannel)
class SensorChannelAdmin(admin.ModelAdmin):
    list_display = ('sensor_type', 'channel')
    list_filter = ('sensor_type', 'channel')
    search_fields = ['channel']


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('sensor_name', 'sensor_id', 'channel', 'location', 'mac_id')
    list_filter = ('channel', 'location')
    search_fields = ['sensor_id', 'sensor_name']


@admin.register(SensorDatabase)
class SensorDatabaseAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'purpose', 'database')
    list_filter = ('sensor', 'purpose', 'database')
    # search_fields = ['sensor']


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('operation_id', 'description')
    # list_filter = ('sensor','purpose','database')
    search_fields = ['operation_id', 'description']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'channel', 'data_source', 'frequency', 'next_run', 'description' )
    list_filter = ('channel', 'data_source', 'frequency', 'next_run')
    search_fields = ['sensor', 'data_source','description']


@admin.register(TaskCondition)
class TaskConditionAdmin(admin.ModelAdmin):
    list_display = ('task', 'Field', 'condition', 'value','string_value')
    list_filter = ('task', 'Field')
    search_fields = ['task', 'Field']


@admin.register(SensorTask)
class SensorTaskAdmin(admin.ModelAdmin):
    list_display = ('task', 'sensor', 'run_date', 'status')
    list_filter = ('task', 'sensor', 'run_date', 'status')
    search_fields = ['task', 'sensor']


@admin.register(ExcludeSensor)
class SensorTaskAdmin(admin.ModelAdmin):
    list_display = ('task', 'sensor')
    list_filter = ('task', 'sensor')
    search_fields = ['task', 'sensor']
