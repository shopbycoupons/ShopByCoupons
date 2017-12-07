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

    tagheader= a['mail']['headers'][1]['value']
    tagvales = b.split(",")
    tagname2 = c[1].split("=")
    tagname1 = c[0].split("=")
    tag1 = tagname1[1]
    tag2 = tagname2[1]


    try:
        status = data['eventType']
    except KeyError:
        status = data['notificationType']
    date = data['mail']['timestamp']

    connection = pymysql.connect(host="localhost",user=proddbuser, passwd=proddbpass, database=proddbname )
    cursor = connection.cursor()
    if status == 'Bounce' or status == 'Complaint' or status == 'Click' or status == 'Open':
        cursor.execute ("""\
            UPDATE email
            SET status=%s, date=%s
            WHERE email=%s
        """, (status, date, eid))
    try:
        cursor.execute("insert into ecamp (id, eid, status, date) values (%s, %s, %s, %s)", (pk, eid, status, date))
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:
            ret = 'pass'
            pass

    complaints = cursor.execute("select complaints from emails_campaign")
    bounces = cursor.execute("select bounces from emails_campaign")
    clicks = cursor.execute("select clicks from emails_campaign")
    opens = cursor.execute("select opens from emails_campaign")
    if status == 'Bounce':
        bounces = bounces + 1
        cursor.execute ("""\
            UPDATE emails_campaign
            SET bounces=%d
            WHERE tag1=%s AND tag2=%s
        """, (bounces, tag1, tag2))

    elif status == 'Complaint':
        complaints = complaints + 1
        cursor.execute ("""\
            UPDATE emails_campaign
            SET complaints=%d
            WHERE tag1=%s AND tag2=%s
        """, (complaints, tag1, tag2))

    elif status == 'Click':
        clicks = clicks + 1
        cursor.execute ("""\
            UPDATE emails_campaign
            SET clicks=%d
            WHERE tag1=%s AND tag2=%s
        """, (clicks, tag1, tag2))

    elif status == 'Open':
        opens = opens + 1
        cursor.execute ("""\
            UPDATE emails_campaign
            SET opens=%d
            WHERE tag1=%s AND tag2=%s
        """, (opens, tag1, tag2))


    connection.commit()
    connection.close()
    return (ret)
