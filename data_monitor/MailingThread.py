import time 
import multiprocessing
import pymysql
import datetime
import smtplib

class MailingThread(multiprocessing.Process):
    def __init__(self):
        super(MailingThread, self).__init__()
        self.exit = multiprocessing.Event()
        self.get_maxid()
        
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
        connection = pymysql.connect(host='10.129.23.22',
                                 user='data_logging',
                                 password='data_logging',
                                 db='data_logging',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

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
        connection = pymysql.connect(host='10.129.23.22',
                                 user='data_logging',
                                 password='data_logging',
                                 db='data_logging',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

        cursor = connection.cursor()

        cursor.execute("SELECT id,run_date,sensor_id, expected, actual,description,mail_to FROM data_logging.meta_sensortask s, meta_task t where s.task_id = t.task_id and  id > %s;",(self.max_id,))
        rec = cursor.fetchall()

        msg = {}

        for x in rec:
            if self.max_id < int(x['id']):
                self.max_id = int(x['id'])
            if x[u'mail_to'] not in msg:
                msg[x[u'mail_to']] =""
            msg[x[u'mail_to']] += "At " + str(x[u'run_date']) + " " + x['sensor_id'] + " " +  x['description'].format(actual = x['actual'], expected = x['expected']) + "\n"
            print "At " + str(x[u'run_date']),x['sensor_id'] , x['description'].format(actual = x['actual'], expected = x['expected'])
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
                    self.send_alert_mail(k,msg[k], "Logging Alert")
            time.sleep(1)
            ctr += 1
            
        print "Mailer Stopped"
