import argparse

import pymysql
#import os
#from os.path import join
import time 
import multiprocessing
#import queue
import datetime
#from Queue import Queue
from MqttEventThread import MqttEventThread
from MailingThread import MailingThread
from MongoDbThread import  MongoDbThread

def runMainProcesses():
    sql1 = "select * from task_list where type = 'Q'"
    sql2 = """select * from task_list t, meta_sensor s where type = 'G'
    and t.channel_id = s.channel_id and next_run < %s """
    sql3 = "update meta_task set next_run = %s where task_id = %s "
    connection = pymysql.connect(host='10.129.23.22',
                                 user='data_logging',
                                 password='data_logging',
                                 db='data_logging',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    # mqtt_q should be a list
    # mqtt_q = multiprocessing.Queue()
    mongo_q = multiprocessing.Queue()
    task_que = multiprocessing.Queue()
    mqttThreads = {}
    mongo_workerCount = 1
    mongoThreads = [None for x in range(mongo_workerCount)]


    quit = False
    valid_response = 'exit'
    print "Type command (exit) to exit."
    mailer = None
    mongoThread = None
    create_mailer = False
    create_mongo = False
    while (quit== False):
        if mailer is None:
            create_mailer = True
        elif not mailer.is_alive():
            create_mailer = True
        if create_mailer:
            print "Create mailer"
            mailer = MailingThread()
            mailer.start()
            create_mailer = False

        if mongoThread is None:
            create_mongo = True
        elif not mongoThread.is_alive():
            create_mongo = True
        if create_mongo:
            print "Create Mongo thread"
            mongoThread = MongoDbThread(mongo_q)
            mongoThread.start()
            create_mongo = False

        cursor = connection.cursor()
        # get the list of task.
        print "executing ", sql1
        cursor.execute(sql1)
        result = cursor.fetchall()

        for t in result:
            print t['type']
            # if MQTT task
            if t['type'] == 'Q':
                flg_create = False
                # Check if the thread for the task is existing
                if t['data_source_id'] in mqttThreads:
                    # Check if the task is running
                    if not mqttThreads[t['data_source_id']].is_alive():
                        flg_create = True
                else:
                    flg_create = True
                # Start the process if required and or if the task as not running
                if flg_create:
                    # create process for the task
                    p = MqttEventThread(t,task_que)
                    mqttThreads[t['data_source_id']] = p
                    p.start()
                    flg_create = False
                task_que.put(t)

        print "executing mongo query", sql2
        t_query = datetime.datetime.now()
        time.sleep(30)
        cursor.execute(sql2,(t_query,))
        result = cursor.fetchall()

        # select all sensor for the task
        update_task = False
        for t in result:
            #print t
            if t['type'] == 'G':
                update_task = True
                next_run = t['next_run']
                if t['frequency'] == 'H':
                    next_run = next_run + datetime.timedelta(seconds=3600)
                task_id = t['task_id']
                # Send messages
                print "put Task", t["next_run"], t["sensor_id"]
                mongo_q.put(t)
        if update_task:
            print task_id, "Set date to ", next_run
            cursor.execute(sql3,(next_run,task_id))
            connection.commit()
            #connection.close()

                # update next_run


        # check the database for and time based task that can be executed
        # send the message to queue and update the task to running

        #user_input = raw_input(">>> ")
        #if (user_input == valid_response):
        #    quit = True
        #    continue

        #time.sleep(5)

    connection.close()
    print "Stopping "
    for task in  mqttThreads:
        mqttThreads[task].stop()
        mqttThreads[task].join()
    mongoThread.stop()
    mongoThread.join()
    mailer.stop()
    mailer.join()

    
def main(args):
    #print(args)
    
    #db_name = "config.sqlite"
    #g_params = dbfn.getParams(db_name)

    parser = argparse.ArgumentParser(description='Smart Meter data selection')
    group1 = parser.add_mutually_exclusive_group(required=False)
    group1.add_argument('-l', action="store_true", dest="list", help="List parameters")
    group1.add_argument('-m', action="store_true", dest="listmeters", help="List meters")
    group1.add_argument('-q', action="store_true", dest="queuecount", help="give que message count")
    group1.add_argument('-r', action="store_true", dest="run", help="Run the program")
    group1.add_argument('-s', action="store", dest="set", help="where SET is <parameter>=<value>")
    group1.add_argument('-a', action="store", dest="add", help="where ADD is <port>,<value>")

    arguments = parser.parse_args()
    #print arguments
    
    if arguments.run:
        print "running !!!"
        runMainProcesses()

        
if __name__ == '__main__':
    import sys
    main(sys.argv[1:]) 