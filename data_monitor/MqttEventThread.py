import time 
import multiprocessing
import paho.mqtt.client as mqtt
import pymysql
import datetime
import Queue

def on_message(client, userdata, msg):
    userdata.process_message(msg.topic, msg.payload)

class MqttEventThread(multiprocessing.Process):
    def __init__(self,parameters,task_que):
        super(MqttEventThread, self).__init__()
        self.params = parameters
        self.exit = multiprocessing.Event()
        self.msgCount = {}
        self.task = {}
        #self.topics = {}

        self.task_que = task_que
        # self.condition = parameters['condition']
        # self.frequency = parameters['frequency']
        # self.field_number = int(parameters['field_number']) -1
        # self.value = parameters['value']
        # self.ignore_count = parameters['ignore_count']
        #self.ignore_count = 2
        self.count_outside = {}
        self.lastMsgData = {}
        self.connected = False
        #if self.condition == 'C':
        #    if self.frequency == 'H':
        #        self.t_next = ((int(time.time() + 1800) / 3600) + 1)

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
        # print "topic received", topic
        t_fields = topic.split("/")
        for t in self.task:
            if self.task[t]['schema'] == t_fields[0] and  self.task[t]['sensor_type_id'] == t_fields[2]:
                self.check_msg_for_task(topic,msg,self.task[t])

    def check_msg_for_task(self,topic,msg,task):
        if task["condition"] == 'I':
            if topic not in self.lastMsgData:
                self.lastMsgData[topic] = 0
                self.count_outside[topic] = 0
            cols = msg.split(",")
            # print cols
            new_value = float(cols[task["field_number"] - 1])
            if self.lastMsgData[topic] + task["value"] > new_value:
                self.count_outside[topic] += 1
                print topic, task["value"], new_value, self.count_outside[topic], task["ignore_count"]
                if self.count_outside[topic] >= task["ignore_count"]:
                    print task["condition"]  , "condition violated ", topic, self.lastMsgData[topic], new_value
                    self.log_event_for_topic(topic,new_value,self.lastMsgData[topic] + task["value"])
                    self.count_outside[topic] = 0
            self.lastMsgData[topic] = new_value

        if task["condition"] in ['=', '!', '<', 'L', '>', 'G']:
            cols = msg.split(",")
            val = float(cols[task["field_number"]])
            result = {
                '=': lambda x, y: x == y,
                '!': lambda x, y: x != y,
                '<': lambda x, y: x < y,
                'L': lambda x, y: x <= y,
                '>': lambda x, y: x > y,
                'G': lambda x, y: x >= y,
            }
            if not result[task["condition"]](val, task["value"]):
                self.count_outside[topic] += 1
                if self.count_outside[topic] >= task["ignore_count"]:
                    print "condition violated ", self.params, topic
                    self.count_outside[topic] = 0

    def stop(self):
        self.exit.set()

    def get_next_queue_message(self):
        try:
            task = self.task_que.get(timeout=0.1)
            #print "received " ,task
            return (task)
        except Queue.Empty:
            return None

    def run(self):
        self.client = mqtt.Client('Monitor_' + self.params['data_source_id'], userdata=self, protocol=mqtt.MQTTv311, clean_session=True)
        # client.on_connect = on_connect
        self.client.on_message = on_message

        self.connected = False
        while not self.connected:
            print "Try to connect to reader MQTT", self.params['ip'], int(self.params['port'])
            try:
                self.client.connect(self.params['ip'], int(self.params['port']), 600)
                self.connected = True
                print "Connected"
                self.client.loop_start()
            except IOError:
                print "Could not Connect"
                time.sleep(1)

        while not self.exit.is_set():
            task = self.get_next_queue_message()
            if task is not None:
                self.add_task(task)
            time.sleep(1)
        print "Reader Stopped"

    def add_task(self, t):
        while not self.connected:
            time.sleep(1)
        if t["task_id"] not in self.task:
            # print "adding MQTT Task", t
            self.task[t["task_id"]] = t
            topic = t['schema'] + '/+/' + t['sensor_type_id'] + "/+"
            # print "Subscribing to:", ":" + topic + ":"
            self.client.subscribe(topic, qos=0)

