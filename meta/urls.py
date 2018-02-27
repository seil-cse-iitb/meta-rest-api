from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /meta/databases
    # url(r'^databases/$', views.databases, name='database'),

    # ex: /meta/sensor_lookup/<path>
    url(r'^sensor_lookup/(?P<channel>.+)/(?P<location>.+)/(?P<sensor_type>.+)/(?P<mac>.+)$', views.sensorLookup_rest),

    # ex: /meta/database/<database name>
    url(r'^database/(?P<database_id>.+)$', views.database_rest),

    # ex: /meta/channel_fields/<channel id>
    url(r'^channel_fields/(?P<channel_id>.+)$', views.channel_fields_rest),

    # ex: /meta/channel/<channel id>
    url(r'^channel/(?P<channel_id>.+)$', views.channel_fields_rest),

    # ex: /meta/channels/
    url(r'^channels/$', views.channels_view),

    # ex: /meta/sensors
    url(r'^sensors/$', views.sensor_list),

    # ex: /meta/sensors/<channel_id>
    url(r'^sensors/(?P<channel_id>.+)$', views.sensor_list_channel),


    # ex: /meta/database/<database name>
    url(r'^sensor/(?P<sensor_id>.+)/$', views.sensor_rest, name='db_id'),

    url(r'^sensor_mac/(?P<sensor_id>.+)/$', views.sensor_rest, name='db_id'),

    # ex: /meta/sensor_types/
    url(r'^sensor_types/$', views.sensorTypes, name='sensors_types'),
    # ex: /meta/sensor_type/<type>
    url(r'^sensor_type/(?P<sensor_type_id>.+)/$', views.sensorType_rest, name='db_id'),

]
