import time
import multiprocessing
import pymysql
import datetime
import Queue
import socket

HOST = "10.129.23.22"
PORT = 1234
def on_message(client, userdata, msg):
    userdata.process_message(msg.topic, msg.payload)

class UdpEventThread(multiprocessing.Process):
    def __init__(self,task_que):
        super(UdpEventThread, self).__init__()
        self.exit = multiprocessing.Event()
        self.msgCount = {}
        self.msgCountTime = {}
        self.task = {}
        #self.topics = {}

        self.task_que = task_que
        self.count_outside = {}
        self.lastMsgData = {}
        self.connected = False
        self.dt_start = datetime.datetime(1970, 1, 1)

        #if self.condition == 'C':
        #    if self.frequency == 'H':
        #        self.t_next = ((int(time.time() + 1800) / 3600) + 1)

    def log_event_for_msg(self, task_id,sensor_id, actual, expected):
        sql1 = "insert into meta_sensortask (task_id,sensor_id,run_date,status,actual, expected) values (%s, %s, %s, %s, %s, %s)"
        connection = pymysql.connect(host='10.129.23.41',
                                     user='data_logging',
                                     password='data_logging',
                                     db='data_logging',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        cursor = connection.cursor()
        # t = tuple(topic.split("/"))
        #print sql0, t
        # cursor.execute(sql0,t)
        # result = cursor.fetchall()

        # get the list of task.
        l =(task_id,str(sensor_id),datetime.datetime.today(),'E', actual, expected)
        #print sql1,l
        cursor.execute(sql1,l)
        connection.commit()
        connection.close()

    def process_next_message(self):
        try:
            # print "process_next_message"

            # recv can throw socket.timeout
            # self.sock.settimeout(10.0)
            # print self.sock
            data =  self.sock.recvfrom(4096)
            msg = data[0][1:-1].split(",")
            # print msg
            self.check_msg_for_task(msg)
        except socket.error, s_msg:
            print 'Socket timeout: ', socket.error, s_msg
            self.connected = False

            # for t in self.task:
        #    if self.task[t]['mac'] == m_fields :
        #        self.check_msg_for_task(t ,msg,self.task[t])

    def check_msg_for_task(self,msg):
        if msg[0] in self.task:
            sensor_task = self.task[msg[0]]
            for task_key in sensor_task:
                topic = msg[0] + '_' + task_key
                task = sensor_task[task_key]
                #if task["condition"] == 'C':
                #    if topic not in self.msgCount:
                #        self.msgCount[topic] = 0
                #        self.msgCountTime[topic] = (task['next_run'] - self.dt_start).total_seconds() - 5.5 * 3600


                if task["condition"] == 'I':
                    if topic not in self.lastMsgData:
                        self.lastMsgData[topic] = 0
                        self.count_outside[topic] = 0
                    # cols = msg.split(",")
                    cols = msg[1:]
                    # print cols
                    new_value = float(cols[task["field_number"] - 1])
                    if self.lastMsgData[topic] + task["value"] > new_value:
                        self.count_outside[topic] += 1
                        print topic, task["value"], new_value, self.count_outside[topic], task["ignore_count"]
                        if self.count_outside[topic] >= task["ignore_count"]:
                            print task["condition"]  , "condition violated ", topic, self.lastMsgData[topic], new_value
                            #self.log_event_for_topic(topic,new_value,self.lastMsgData[topic] + task["value"])
                            self.count_outside[topic] = 0
                    self.lastMsgData[topic] = new_value

                if task["condition"] in ['=', '!', '<', 'L', '>', 'G']:
                    # print "Checking for integer condition"
                    # cols = msg[1:]
                    if len (msg) > task["field_number"]:
                        val = int(msg[task["field_number"]])
                        result = {
                            '=': lambda x, y: x == y,
                            '!': lambda x, y: x != y,
                            '<': lambda x, y: x < y,
                            'L': lambda x, y: x <= y,
                            '>': lambda x, y: x > y,
                            'G': lambda x, y: x >= y,
                        }
                        # print task["condition"], val, task["value"]
                        if result[task["condition"]](val, task["value"]):
                            if topic not in self.count_outside:
                                self.count_outside[topic] = 0
                            self.count_outside[topic] += 1
                            if self.count_outside[topic] >= task["ignore_count"]:
                                print "condition violated ", topic
                                self.count_outside[topic] = 0
                                self.log_event_for_msg(task_key,msg[0], val, task["value"])

                if task["condition"] in ['S', 'T']:
                    # print "Checking for string condition"
                    # cols = msg[1:]
                    if len(msg) > task["field_number"]:
                        # print task["field_number"],cols
                        val = msg[task["field_number"] ]
                        # print val, task["string_value"]
                        condition_violated = False
                        if task["condition"] == 'T':
                            if val !=  task["string_value"]:
                                print "not same " , val ,task["string_value"]
                                condition_violated = True
                        if task["condition"] == 'S':
                            if val == task["string_value"]:
                                condition_violated = True
                        if condition_violated:
                            if topic not in self.count_outside:
                                self.count_outside[topic] = 0
                            self.count_outside[topic] += 1
                            print "condition violated ", topic
                            if self.count_outside[topic] >= task["ignore_count"]:
                                self.count_outside[topic] = 0
                                self.log_event_for_msg(task_key,msg[0], val, task["string_value"])




    def stop(self):
        self.exit.set()

    def get_next_task(self):
        try:
            task = self.task_que.get(timeout=0.1)
            #print "received " ,task
            return (task)
        except Queue.Empty:
            return None

    def run(self):
        while not self.exit.is_set():
            if not self.connected :
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    # sock.settimeout(5.0)
                    #self.conn, addr = sock.accept()
                except socket.error, msg:
                    print 'Failed to create socket. Error Code : ',socket.error, msg
                    continue
                print '******** Socket created'

                # Bind socket to local host and port
                print "********* Binding To", HOST, PORT
                try:
                    self.sock.bind((HOST, PORT))
                except socket.error, msg:
                    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                    # sys.exit()
                    continue
                self.connected = True

                print '********* Socket bind complete'

            task = self.get_next_task()
            if task is not None:
                self.add_task(task)
            self.process_next_message()

        # self.conn.close()

        print "Reader Stopped"

    def add_task(self, t):
        while not self.connected:
            time.sleep(1)
        if t["sensor_id"] not in self.task:
            # print "adding UDP sensor",t["sensor_id"]
            self.task["sensor_id"] = {}
        sensor_task = self.task["sensor_id"]
        #if t["task_id"]  not in sensor_task:
        #    print "adding UDP Task", t
        sensor_task[t["task_id"]] = t
        self.task[t["sensor_id"]] = sensor_task

