from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from .serializers import *

from .models import Database, SensorChannel ,Sensor ,SensorType, DataField
# Create your views here.
from django.http import HttpResponse
# added by sapan
from functions import send_mail


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@api_view()
@permission_classes((permissions.AllowAny,))
def sensorLookup_rest(request, channel,location,sensor_type,mac):
    """
        Query sensor by channel, location, sensor_type and mac
    """
    ch = SensorChannel.objects.filter(channel=channel,sensor_type=sensor_type)
    if len(ch) == 0:
        return HttpResponse("Channel information not available")
    s = Sensor.objects.filter(location=location, channel= ch[0].pk, mac_id = mac)
    if len(s) == 0:
        return HttpResponse('{"error":"Sensor information not available"}')
    serializer = SensorSerializer(s[0])
    return JSONResponse(serializer.data)


def database_rest(request, database_id):
    db = Database.objects.filter(database_id=database_id)
    if len(db) == 0:
        return HttpResponse('{"error":"Database information not available"}')
    serializer = DatabaseSerializer(db[0])
    return JSONResponse(serializer.data)

@api_view()
@permission_classes((permissions.AllowAny,))
def channel_fields_rest(request,channel_id):
    """
        Display list of fields present in the MQTT message for all sensors on this channel. The order of fields is important. 
    """
    df = DataField.objects.filter(sensor_type=channel_id)
    if len(df) == 0:
        return HttpResponse('{"error":"Field information not available"}')
    serializer = FieldSerializer(df,many=True)
    return JSONResponse(serializer.data)

@api_view()
@permission_classes((permissions.AllowAny,))
def channel_view(request,channel_id):
    """
        Display list of all channels
    """
    df = SensorChannel.objects.filter(id=channel_id)
    if len(df) == 0:
        return HttpResponse('{"error":"Field information not available"}')
    serializer = ChannelSerializer(df,many=True)
    return JSONResponse(serializer.data)
    
@api_view()
@permission_classes((permissions.AllowAny,))
def channels_view(request):
    """
        Display list of all channels
    """
    df = SensorChannel.objects.all()
    if len(df) == 0:
        return HttpResponse('{"error":"Field information not available"}')
    serializer = ChannelSerializer(df,many=True)
    return JSONResponse(serializer.data)


def databases(request):
    databases = Database.objects.all()
    context = {'database_list': databases}
    return render(request, 'meta/databases.html', context)

@api_view()
@permission_classes((permissions.AllowAny,))
def sensors(request):
    sensor = Sensor.objects.all()
    context = {'sensor_list': sensor}
    return render(request, 'meta/sensors.html', context)

@api_view()
@permission_classes((permissions.AllowAny,))
def sensor_rest(request, sensor_id):
    return HttpResponse("You're looking at sensor %s." % sensor_id)

def sensorTypes(request):
    sensor_type = SensorType.objects.all()
    context = {'sensor_type_list': sensor_type}
    return render(request, 'meta/sensor_types.html', context)


def sensorType_rest(request, sensor_type_id):
    return HttpResponse("You're looking at sensor Type %s." % sensor_type_id)

@api_view()
@permission_classes((permissions.AllowAny,))
def sensor_list(request):
    """
    List all sensors.
    """
    if request.method == 'GET':
        sensor = Sensor.objects.all()
        serializer = SensorSerializer(sensor, many=True)
        return JSONResponse(serializer.data)

@api_view()
@permission_classes((permissions.AllowAny,))
def sensor_list_channel(request,channel_id):
    """
    List all sensors belonging to this channel.
    """
    df = Sensor.objects.filter(channel=channel_id)
    if len(df) == 0:
        return HttpResponse('{"error":"Field information not available"}')
    serializer = SensorSerializer(df,many=True)
    return JSONResponse(serializer.data)

# view_mail function added by sapan
def views_mail(request):
    to = ""
    body = ""
    subject = ""
    if request.method == 'GET':
        to = request.GET.get('to',"")
        body = request.GET.get('body',"")
        subject = request.GET.get('subject',"")
    elif request.method == 'POST':
        to = request.POST.get('to',"")
        body = request.POST.get('body',"")
        subject = request.POST.get('subject',"")

    message =""
    if to=="":
        message= "Failed!! parameter 'to' required"
    elif body=="":
        message = "Failed!! parameter 'body' required"
    elif subject=="":
        message= "Failed!! parameter 'subject' required"

    if to !="" and body !=""  and subject !="" :
        send_mail(to, body, subject)
        return HttpResponse("Success!!<br><br>To: " + to + "<br>Subject: " + subject + "<br>Body: " + body)
    else:
        return HttpResponse(message+"<br><br>To: " + to + "<br>Subject: " + subject + "<br>Body: " + body)
