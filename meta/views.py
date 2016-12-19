from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from .serializers import *

from .models import Database, SensorChannel ,Sensor ,SensorType, DataField
# Create your views here.
from django.http import HttpResponse

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def sensorLookup_rest(request, channel,location,sensor_type,mac):
    ch = SensorChannel.objects.filter(channel=channel,sensor_type=sensor_type)
    if len(ch)==0 :
        return HttpResponse("Channel information not available")
    s = Sensor.objects.filter(location=location, channel= ch[0].pk, mac_id = mac)
    if len(s)==0 :
        return HttpResponse('{"error":"Sensor information not available"}')
    serializer = SensorSerializer(s[0])
    return JSONResponse(serializer.data)


def database_rest(request, database_id):
    db = Database.objects.filter(database_id=database_id)
    if len(db)==0 :
        return HttpResponse('{"error":"Database information not available"}')
    serializer = DatabaseSerializer(db[0])
    return JSONResponse(serializer.data)

def channel_fields_rest(request,channel_id):
    df = DataField.objects.filter(sensor_type=channel_id)
    if len(df)==0 :
        return HttpResponse('{"error":"Field information not available"}')
    serializer = FieldSerializer(df,many=True)
    return JSONResponse(serializer.data)

def databases(request):
    databases = Database.objects.all()
    context = {'database_list': databases}
    return render(request, 'meta/databases.html', context)


def sensors(request):
    sensors = Sensor.objects.all()
    context = {'sensor_list': sensors}
    return render(request, 'meta/sensors.html', context)

def sensor_rest(request, sensor_id):
    return HttpResponse("You're looking at sensor %s." % sensor_id)


def sensorTypes(request):
    sensor_type = SensorType.objects.all()
    context = {'sensor_type_list': sensor_type}
    return render(request, 'meta/sensor_types.html', context)

def sensorType_rest(request, sensor_type_id):
    return HttpResponse("You're looking at sensor Type %s." % sensor_type_id)


def sensor_list(request):
    """
    List all code sensors, or create a new snippet.
    """
    if request.method == 'GET':
        sensor = Sensor.objects.all()
        serializer = SensorSerializer(sensor, many=True)
        return JSONResponse(serializer.data)
