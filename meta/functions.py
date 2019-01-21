import smtplib
#this file added by sapan

user = "seil"
pwd = "seilers"


def init_mail():
    smtpserver = smtplib.SMTP("smtp.cse.iitb.ac.in", 25)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.esmtp_features['auth'] = 'LOGIN DIGEST-MD5 PLAIN'
    return smtpserver


def send_mail(to, body, subject):
    smtpserver = init_mail()
    smtpserver.login(user, pwd)
    header = "To:" + to + '\n' + 'From: ' + user + '@cse.iitb.ac.in\n' + 'Subject:' + subject + '\n'
    msg = header + '\n' + body + '\n\n'
    smtpserver.sendmail(user, to, msg)
    smtpserver.close()
