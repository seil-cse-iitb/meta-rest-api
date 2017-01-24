import time 
import multiprocessing
import pymysql
import datetime
from pymongo import MongoClient
import json
import Queue

class MongoDbThread(multiprocessing.Process):
    def __init__(self,mongo_q):
        super(MongoDbThread, self).__init__()
        # self.params = parameters
        self.exit = multiprocessing.Event()
        self.qname = mongo_q
        self.sensor_task_count = {}
        self.msgCount = {}
        self.lastMsgData = {}
        print "Mongo init done"

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
        # print sql0, t
        cursor.execute(sql0,t)
        result = cursor.fetchall()
        sensor_id = result[0]['sensor_id']

        # get the list of task.
        l =(self.params['task_id'],str(sensor_id),datetime.datetime.today(),'E', actual, expected)
        # print sql1,l
        cursor.execute(sql1,l)
        connection.commit()
        connection.close()

    def log_event_for_task(self, task, actual):
        #sql0 = "SELECT sensor_id FROM data_logging.meta_sensor s, meta_sensorchannel c where channel = %s and "
        #sql0 += "location = %s and s.channel_id = c.id and sensor_type_id = %s and mac_id = %s "

        sql1 = "insert into meta_sensortask (task_id,sensor_id,run_date,status,actual, expected) values (%s, %s, %s, %s, %s, %s)"
        connection = pymysql.connect(host='10.129.23.22',
                                     user='data_logging',
                                     password='data_logging',
                                     db='data_logging',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        cursor = connection.cursor()

        # get the list of task.
        l =(task['task_id'],task['sensor_id'],task['next_run'],'E', actual, task['value'])
        # print sql1,l
        cursor.execute(sql1,l)
        connection.commit()
        connection.close()

        
    def process_task(self, task, date_Range):
        mongo =   MongoClient(task['ip'],int(task['port'])) 
        # print "checking mongo DB" ,task['schema'], task['sensor_id'],
        db = mongo[task['schema']]
        table = db[task['sensor_id']]
        key = task['task_id'] + task['sensor_id']
        
        # print "key is ", key 
        if task["condition"] == 'C':
            # print key, date_Range,
            row_count = table.find({"$and": [{"TS": {"$gt": date_Range[0]}},{"TS": {"$lt": date_Range[1]}}]},
                             { "TS": 1} ).count()
            # print row_count
            if row_count < task['value'] - task['margin'] :
                if key not in self.sensor_task_count:
                    self.sensor_task_count[key] = 0
                self.sensor_task_count[key] += 1
                # print "mongo task", task
                if self.sensor_task_count[key] >= task["ignore_count"]:
                    # print "condition violated ", task, row_count
                    # self.qname.put((topic,msg))
                    self.log_event_for_task(task,row_count)
                    self.sensor_task_count[key] = 0
            else:
                self.sensor_task_count[key] = 0

    def get_next_queue_message(self):
        try:
            task = self.qname.get(timeout=0.1)
            # print "received " ,task
            return (task)
        except Queue.Empty:
            return None

                
    def stop(self):
        self.exit.set()
        
    def run(self):
        while not self.exit.is_set():
            task = self.get_next_queue_message()
            if task is not None:
                # print "Mongo task Received ", task["next_run"], task["sensor_id"]
                dt_start = datetime.datetime(1970, 1, 1)
                # print task['next_run'],dt_start
                ts_2 = (task['next_run'] - dt_start).total_seconds() - 5.5 * 3600
                # print ts_2

                if task['frequency'] == 'H':
                    period = [ ts_2 - 3600, ts_2]
                self.process_task(task,period)

                
            time.sleep(0.1)
        print "Reader Stopped"
