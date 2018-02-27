import time 
import multiprocessing
import datetime
import Queue
import MySQLdb as pymysql

from MqttEventThread import MqttEventThread
from MailingThread import MailingThread
from MongoDbThread import  MongoDbThread


class ControllerThread(multiprocessing.Process):
    def __init__(self):
        super(ControllerThread, self).__init__()
        self.exit = multiprocessing.Event()

        self.mqttThreads = {}
        self.udpThreads = {}
        self.mailerThread = None
        self.mongoThread = None
        #mongoThresdCount = 1
        #self.mongoThreads = [None for x in range(mongoThresdCount)]


    def stop(self):
        self.exit.set()

    def run(self):
        print "Run ControllerThread"
        self.connection = pymysql.connect(host='10.129.23.41',
                                     user='data_logging',
                                     passwd='data_logging',
                                     db='data_logging')

        self.mongo_q = multiprocessing.Queue()
        self.mqtt_q = multiprocessing.Queue()
        # self.udp_q = multiprocessing.Queue()

        while not self.exit.is_set():
            print "Disp 1"
            self.dispatch_mongo_task()
            print "Disp 2"
            self.dispatch_mqtt_task()
            print "Disp 3"
            # self.dispatch_udp_task()
            print "Disp 4"
            self.dispatch_Mail()
            print "Disp done"
            time.sleep(6)

        print "Stopping mail Threads"
        print self.mailerThread
        self.mailerThread.stop()
        self.mailerThread.join()
        print "Stopping mongo Threads"
        self.mongoThread.stop()
        self.mongoThread.join()

        print "Stopping MQTT Threads"
        for t in self.mqttThreads:
            self.mqttThreads[t].stop()
            self.mqttThreads[t].join()


    def dispatch_mongo_task(self):
        sql2 = """select * from task_list t, meta_sensor s where type = 'G'
        and t.channel_id = s.channel_id and next_run < %s """
        sql3 = "update meta_task set next_run = %s where task_id = %s "

        print "Mongo Thread", self.mongoThread


        create_mongo = False
        if self.mongoThread is None:
            create_mongo = True
        # elif not self.mongoThread.is_alive():
        #    create_mongo = True
        if create_mongo:
            print "Create Mongo thread"
            self.mongoThread = MongoDbThread(self.mongo_q)
            self.mongoThread.start()
            create_mongo = False

        print "Create cursor"
        cursor = self.connection.cursor()
        print "executing mongo query", sql2
        t_query = datetime.datetime.now()
        # change it to time computation
        time.sleep(5)
        cursor.execute(sql2, (t_query,))
        print "executed"
        result = cursor.fetchall()
        print "fetched"

        # select all sensor for the task
        for t in result:
            update_task = False
            print t
            if t['type'] == 'G':
                update_task = True
                next_run = t['next_run']
                if t['frequency'] == 'H':
                    next_run = next_run + datetime.timedelta(seconds=3600)
                task_id = t['task_id']
                # Send messages
                print "put Task", t["next_run"], t["sensor_id"]
                self.mongo_q.put(t)

            if update_task:
                print task_id, "Set date to ", next_run
                cursor.execute(sql3, (next_run, task_id))
                self.connection.commit()


    def dispatch_mqtt_task(self):
        sql1 = "select * from task_list where type = 'Q'"
        cursor = self.connection.cursor()
        # get the list of task.
        # print "executing ", sql1
        cursor.execute(sql1)
        result = cursor.fetchall()

        for t in result:
            # print t['type']
            # if MQTT task
            if t['type'] == 'Q':
                flg_create = False
                # Check if the thread for the task is existing
                if t['data_source_id'] in self.mqttThreads:
                    # Check if the task is running
                    if not self.mqttThreads[t['data_source_id']].is_alive():
                        flg_create = True
                else:
                    flg_create = True
                # Start the process if required and or if the task as not running
                if flg_create:
                    # create process for the task
                    p = MqttEventThread(t, self.mqtt_q)
                    self.mqttThreads[t['data_source_id']] = p
                    p.start()
                    flg_create = False
                self.mqtt_q.put(t)



    def dispatch_Mail(self):
        create_mailer = False
        if self.mailerThread is None:
            create_mailer = True
        elif not self.mailerThread.is_alive():
            create_mailer = True
        if create_mailer:
            print "Create mailer",
            self.mailerThread = MailingThread()
            self.mailerThread.start()
            print "Created", self.mailerThread

