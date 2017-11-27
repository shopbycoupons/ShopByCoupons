from __future__ import absolute_import, unicode_literals

import json
import pymysql
from appconfig import *
from config import *


from celery import Celery
from celery import shared_task
from celery import app

@shared_task
def send_email(pk, msg):
    ret='added'
    stat = msg
    connection = pymysql.connect(host="localhost",user=proddbuser, passwd=proddbpass, database=proddbname )
    cursor = connection.cursor()
    try:
        cursor.execute("insert into ecamp (id, status) values (%s, %s, %s, %s)", (pk, stat))
        connection.commit()
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:
            ret = 'pass'
            pass

    connection.close()
    return (ret)
