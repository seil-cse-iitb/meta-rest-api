import argparse
import time
from ControllerThread import ControllerThread

def runMainProcesses():
    valid_response = 'exit'
    print "Type command (exit) to exit."
    # mailer = None
    controlThread = None
    # create_mailer = False
    create_controller = False
    quit = False
    while (quit== False):
        if controlThread is None:
            create_controller = True
        elif not controlThread.is_alive():
            create_controller = True
        if create_controller:
            print "Create controller"
            controlThread = ControllerThread()
            controlThread.start()
            create_controller = False

        user_input = raw_input(">>> ")
        if (user_input == valid_response):
            quit = True
            continue

        time.sleep(1)

    print "Stopping "
    controlThread.stop()
    controlThread.join()

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