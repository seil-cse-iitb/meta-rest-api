import time 
import multiprocessing
import MySQLdb as pymysql
import datetime
import smtplib

class MailingThread(multiprocessing.Process):
    def __init__(self):
        print "mailer init start"
        super(MailingThread, self).__init__()
        self.exit = multiprocessing.Event()
        self.get_maxid()
        print "mailer init done"
        
    def init_mail(self):
        smtpserver = smtplib.SMTP("smtp.cse.iitb.ac.in",25)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()
        smtpserver.esmtp_features['auth'] = 'LOGIN DIGEST-MD5 PLAIN'
        return smtpserver

    def close_mail_connection(self,smtpserver):
        smtpserver.close()

    def get_maxid(self):
        self.connection = pymysql.connect(host='10.129.23.41',
                                     user='data_logging',
                                     passwd='data_logging',
                                     db='data_logging')

        cursor = connection.cursor()

        cursor.execute("select max_id from meta_stat")
        rec = cursor.fetchall()
        self.max_id = rec[0]['max_id']


    def send_alert_mail(self,to,body,subject):
        smtpserver = self.init_mail()
        user = "rohitg"
        pwd = "rohitg*"
        smtpserver.login(user,pwd)
        header = "To:" + to + '\n' + 'From: ' + user +'@cse.iitb.ac.in\n' + 'Subject:'+subject+'\n'
        msg = header + '\n' + body + '\n\n'

        smtpserver.sendmail(user,to,msg)
        self.close_mail_connection(smtpserver)
        
    def get_message(self):
        self.connection = pymysql.connect(host='10.129.23.41',
                                     user='data_logging',
                                     passwd='data_logging',
                                     db='data_logging')

        cursor = connection.cursor()

        sql1 = """SELECT id,run_date,x.sensor_name, expected, actual,description,mail_to
            FROM data_logging.meta_sensortask s, meta_task t, meta_sensor x
            where (x.sensor_id) not in ( select sensor_id from meta_excludesensor )
            and s.task_id = t.task_id and s.sensor_id = x.sensor_id and  id > %s;"""

        cursor.execute(sql1,(self.max_id,))
        rec = cursor.fetchall()

        msg = {}

        for x in rec:
            if self.max_id < int(x['id']):
                self.max_id = int(x['id'])
            for address in x[u'mail_to'].split(","):
				
				if address not in msg:
					msg[address] =""
				msg[address] += "At " + str(x[u'run_date']) + " " + str(x['id']) + " " + x['sensor_name'] + " " +  x['description'].format(actual = x['actual'], expected = x['expected']) + "\n"
				print "At " + str(x[u'run_date']),x['sensor_name'] , x['description'].format(actual = x['actual'], expected = x['expected'])
        print "update counter to ",  self.max_id
        cursor.execute("update meta_stat set max_id = %s", (self.max_id,))
        connection.commit()
        connection.close()
        return msg
    
    def stop(self):
        self.exit.set()
        
    def run(self):
       
        ctr = 0
        while not self.exit.is_set():
            # print ctr
            if ctr >= 60:
                ctr = 0
                msg = self.get_message()
                for k in msg:
                    self.send_alert_mail(k,msg[k], "Data logging issue(s)")
            time.sleep(1)
            ctr += 1
            # time.sleep(1)
        print "Mailer Stopped"
