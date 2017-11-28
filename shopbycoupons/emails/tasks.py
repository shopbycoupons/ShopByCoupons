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
    eid = c[40:80]
    status = c[:10]
    date = c[20:40]

    connection = pymysql.connect(host="localhost",user=proddbuser, passwd=proddbpass, database=proddbname )
    cursor = connection.cursor()
    try:
        cursor.execute("insert into ecamp (id, eid, status, date) values (%s, %s, %s, %s)", (pk, eid, status, date))
        connection.commit()
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:
            ret = 'pass'
            pass

    connection.close()
    return (ret)
