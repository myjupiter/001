#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import re
# from datetime import datetime, timedelta
import sys
import urllib
import json
import requests
import pprint
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

def update(mail):
    url = 'https://vernal-acrobat-149911.appspot.com/message_update'
    data = dict(
        key=mail.id,
    )
    r = requests.post(url, data=data, allow_redirects=True)
    print r.content

def sendmail(mail):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = mail.subject
    part1 = MIMEText(mail.body, "plain", "utf-8")
    msg.attach(part1)
    msg["From"] = "%s" % mail.source
    msg["To"] = "%s" % mail.to
    p = Popen(["/usr/sbin/sendmail", "-t", "-f kdtv@xxx.com", "-oi"], stdin=PIPE)
    p.communicate(msg.as_string())
    
    update(mail)    
    return
    
if '__main__' == __name__:
    class Obj(object):
        pass

    global mail
    mail = Obj()

    url = "https://vernal-acrobat-149911.appspot.com/mail_queue"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    # print data.get('found')
    if data.get('found')=='yes':
        json_data=data.get('out')
        # pprint.pprint(json_data)
        for i, v in list(enumerate(json_data)):
            mail.id=v.get('id')
            line=v.get('to')
            # print line
            # print mail.id
            mail_valid=re.findall(r'[\w\.-]+@[\w\-]+[\.]+[\w\.]+', line)
            if len(mail_valid)==1:
                print mail_valid[0]
                print
                print "---"
                # mail.body = "\n%s" % v.get('body')
                # mail.source = v.get('source')
                # mail.subject = v.get('subject')
                # mail.to=v.get('to')
                # print mail.to
                # sendmail(mail)

                # if v.get('post')=='event':
                if True:
                    body = u"\nชื่อไอดี:\n%s\n\nข้อความ/รูปภาพ:\n%s" % (v.get('name'), v.get('message'))
                    body = body.encode('utf-8')
                    mail.body = body
                    mail.source = v.get('source')
                    mail.subject = v.get('subject')
                    mail.to=mail_valid[0]
                    sendmail(mail)

                # if v.get('post')=='confirm':
                #     fb_message_id=v.get('fb_message_id').split("_")[0]
                #     mail.body = "\nhttps://fb.com/xxx/posts/%s\n\n%s\n\nhttps://fb.com/%s" % ( v.get('fb_message_id' ), v.get('fb_name'), v.get('fb_id') )
                #     mail.source = "Confirm <confirm@xxx.com>"
                #     mail.subject = v.get('fb_message')
                #     mail.to="confirm@xxx.com"
                #     sendmail(mail)

