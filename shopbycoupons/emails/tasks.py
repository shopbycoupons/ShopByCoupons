from __future__ import absolute_import, unicode_literals

import json
import pymysql
from appconfig import *
from config import *


from celery import Celery
from celery import shared_task
from celery import app

@shared_task
def send_email(id, c):
    ret='added'
    pk = id
    data = json.loads(c)
    eid = data['mail']['destination']

    try:
        status = data['eventType']
    except KeyError:
        status = data['notificationType']
    date = data['mail']['timestamp']

    connection = pymysql.connect(host="localhost",user=proddbuser, passwd=proddbpass, database=proddbname )
    cursor = connection.cursor()
    if status == 'Bounce' or status == 'Complaint':
        cursor.execute ("""
            UPDATE email
            SET status=%s, date=%s
            WHERE email=%s
        """, (status, date, email))
    try:
        cursor.execute("insert into ecamp (id, eid, status, date) values (%s, %s, %s, %s)", (pk, eid, status, date))
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:
            ret = 'pass'
            pass
    connection.commit()
    connection.close()
    return (ret)
