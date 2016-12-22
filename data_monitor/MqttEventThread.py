import time 
import multiprocessing
import paho.mqtt.client as mqtt
import pymysql
import datetime

def on_message(client, userdata, msg):
    userdata.process_message(msg.topic, msg.payload)

class MqttEventThread(multiprocessing.Process):
    def __init__(self,parameters):
        super(MqttEventThread, self).__init__()
        self.params = parameters
        self.exit = multiprocessing.Event()
        self.msgCount = {}
        self.condition = parameters['condition']
        self.frequency = parameters['frequency']
        self.field_number = int(parameters['field_number']) -1
        self.value = parameters['value']
        self.ignore_count = parameters['ignore_count']
        #self.ignore_count = 2
        self.count_outside = {}
        self.lastMsgData = {}

        if self.condition == 'C':
            if self.frequency == 'H':
                self.t_next = ((int(time.time() + 1800) / 3600) + 1)

    def log_event_for_topic(self, topic, actual, expected):
        sql0 = "SELECT sensor_id FROM data_logging.meta_sensor s, meta_sensorchannel c where channel = %s and "
        sql0 += "location = %s and s.channel_id = c.id and sensor_type_id = %s and mac_id = %s "

        sql1 = "insert into meta_sensortask (task_id,sensor_id,run_date,status,actual, expected) values (%s, %s, %s, %s, %s, %s)"
        connection = pymysql.connect(host='10.129.23.22',
                                     user='data_logging',
                                     password='data_logging',
                                     db='data_logging',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        cursor = connection.cursor()
        t = tuple(topic.split("/"))
        #print sql0, t
        cursor.execute(sql0,t)
        result = cursor.fetchall()
        sensor_id = result[0]['sensor_id']

        # get the list of task.
        l =(self.params['task_id'],str(sensor_id),datetime.datetime.today(),'E', actual, expected)
        #print sql1,l
        cursor.execute(sql1,l)
        connection.commit()
        connection.close()


    def process_message(self, topic, msg):
        if topic not in self.msgCount:
            self.msgCount[topic] = 0
            self.count_outside[topic] = 0
            self.lastMsgData[topic] = 0
        if self.condition  == 'C':
            self.msgCount[topic] += 1
            if self.frequency == 'H':
                if int((time.time() + 1800) / 3600) == self.t_next:
                    self.t_next += 1
                    if self.value < self.msgCount[topic]:
                        self.count_outside[topic] += 1
                        print self.params, topic, self.count_outside[topic], self.ignore_count
                        if self.count_outside[topic] >= self.ignore_count:
                            print self.condition , "condition violated ", self.params, topic

                            # self.qname.put((topic,msg))
                            self.count_outside[topic] = 0
                    else:
                        self.count_outside[topic] = 0
                    self.msgCount[topic] = 0

        if self.condition == 'I':
            cols = msg.split(",")
            new_value = float(cols[self.field_number])
            if self.lastMsgData[topic] + self.value > new_value:
                self.count_outside[topic] += 1
                print topic, self.value, new_value, self.count_outside[topic], self.ignore_count
                if self.count_outside[topic] >= self.ignore_count:
                    print self.condition  , "condition violated ", topic, self.lastMsgData[topic], new_value
                    self.log_event_for_topic(topic,new_value,self.lastMsgData[topic] + self.value)
                    self.count_outside[topic] = 0
            self.lastMsgData[topic] = new_value

        if self.condition in ['=', '!', '<', 'L', '>', 'G']:
            cols = msg.split(",")
            val = float(cols[self.field_number])
            result = {
                '=': lambda x, y: x == y,
                '!': lambda x, y: x != y,
                '<': lambda x, y: x < y,
                'L': lambda x, y: x <= y,
                '>': lambda x, y: x > y,
                'G': lambda x, y: x >= y,
            }
            if not result[self.condition](val, self.value):
                self.count_outside[topic] += 1
                if self.count_outside[topic] >= self.ignore_count:
                    print "condition violated ", self.params, topic
                    self.count_outside[topic] = 0

    def stop(self):
        self.exit.set()
        
    def run(self):
        client = mqtt.Client('Monitor_' + self.params['task_id'], userdata=self, protocol=mqtt.MQTTv311, clean_session=False)
        # client.on_connect = on_connect
        client.on_message = on_message

        connected = False
        while not connected:
            print "Try to connect to reader MQTT", self.params['ip'], int(self.params['port'])
            try:
                client.connect(self.params['ip'], int(self.params['port']), 600)
                connected = True
            except IOError:
                print "Could not Connect"
                time.sleep(1)

        topic = self.params['schema'] + '/+/' + self.params['sensor_type_id'] + "/+"
        print "Subscribing to:", ":" + topic + ":"
        client.subscribe(topic, qos=1)

        client.loop_start()

        while not self.exit.is_set():
            time.sleep(1)
        print "Reader Stopped"
