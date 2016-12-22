import argparse

import pymysql
#import os
#from os.path import join
import time 
import multiprocessing
#import queue
#from Queue import Queue
from MqttEventThread import MqttEventThread
from MailingThread import MailingThread

def runMainProcesses():
    sql1 = "select * from task_list"
    connection = pymysql.connect(host='10.129.23.22',
                                 user='data_logging',
                                 password='data_logging',
                                 db='data_logging',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    q = multiprocessing.Queue()
    mqttThreads = {}
    quit = False
    valid_response = 'exit'
    print "Type command (exit) to exit."
    mailer = None
    while (quit== False):
        cursor = connection.cursor()
        # get the list of task.
        print "executing ", sql1
        cursor.execute(sql1)
        result = cursor.fetchall()
    
        if mailer is None:
            flg_create = True
        elif not mailer.is_alive():
            flg_create = True
        if flg_create:
            mailer = MailingThread()
            mailer.start()

        
        for t in result:
            print t['type']
            # if MQTT task
            if t['type'] == 'Q':
                flg_create = False
                # Check if the thread for the task is existing
                if t['task_id'] in mqttThreads:
                    # Check if the task is running
                    if not mqttThreads[t['task_id']].is_alive():
                        flg_create = True
                else:
                    flg_create = True
                # Start the process if required and or if the task as not running
                if flg_create:
                    # create process for the task
                    p = MqttEventThread(t)
                    mqttThreads[t['task_id']] = p
                    p.start()


        # get the list of mongo threads.
        # Check if the thread is existing
        # Check if the task is running
        # Start the process if required and se all the task send to this thread as not running

        # check the database for and time based task that can be executed
        # send the message to queue and update the task to running

        user_input = raw_input(">>> ")
        if (user_input == valid_response):
            quit = True
            continue

        time.sleep(60)

    connection.close()
    print "Stopping "
    for task in  mqttThreads:
        mqttThreads[task].stop()
        mqttThreads[task].join()
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