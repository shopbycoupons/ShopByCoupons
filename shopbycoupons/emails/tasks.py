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

    datastr = str(data)
    tagheader= data['mail']['headers'][1]['value']
    tagvalues = tagheader.split(",")
    tagname2 = tagvalues[1].split("=")
    tagname1 = tagvalues[0].split("=")
    tag1 = tagname1[1]
    tag2 = tagname2[1]


    try:
        status = data['eventType']
    except KeyError:
        status = 'Avoidable'
    date = data['mail']['timestamp']

    connection = pymysql.connect(host="localhost",user=proddbuser, passwd=proddbpass, database=proddbname )
    cursor = connection.cursor()

    cursor.execute("insert into edump (id, dump) values (%s, %s)", (pk, datastr))

    if status == 'Bounce' or status == 'Complaint' or status == 'Click' or status == 'Open':
        cursor.execute ("""\
            UPDATE email
            SET status=%s, date=%s
            WHERE email=%s
        """, (status, date, eid))

    cursor.execute("select complaints from emails_campaign where tag1=%s and tag2=%s", (tag1, tag2))
    complaint = cursor.fetchall()
    complaints = complaint[0][0]

    cursor.execute("select bounces from emails_campaign where tag1=%s and tag2=%s", (tag1, tag2))
    bounce = cursor.fetchall()
    bounces = bounce[0][0]

    cursor.execute("select clicks from emails_campaign where tag1=%s and tag2=%s", (tag1, tag2))
    click = cursor.fetchall()
    clicks = click[0][0]

    cursor.execute("select opens from emails_campaign where tag1=%s and tag2=%s", (tag1, tag2))
    opened = cursor.fetchall()
    opens = opened[0][0]

    if status == 'Avoidable':
        ret = 'pass'
    else:
        try:
            cursor.execute("insert into ecamp (id, eid, status, date) values (%s, %s, %s, %s)", (pk, eid, status, date))

            if status == 'Bounce':
                bounces = bounces + 1
                cursor.execute ("""\
                    UPDATE emails_campaign
                    SET bounces=%s
                    WHERE tag1=%s AND tag2=%s
                """, (int(bounces), tag1, tag2))

            elif status == 'Complaint':
                complaints = complaints + 1
                cursor.execute ("""\
                    UPDATE emails_campaign
                    SET complaints=%s
                    WHERE tag1=%s AND tag2=%s
                """, (int(complaints), tag1, tag2))

            elif status == 'Click':
                clicks = clicks + 1
                cursor.execute ("""\
                    UPDATE emails_campaign
                    SET clicks=%s
                    WHERE tag1=%s AND tag2=%s
                """, (int(clicks), tag1, tag2))

            elif status == 'Open':
                opens = opens + 1
                cursor.execute ("""\
                    UPDATE emails_campaign
                    SET opens=%s
                    WHERE tag1=%s AND tag2=%s
                """, (int(opens), tag1, tag2))

        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062:
                ret = 'pass'
                pass




    connection.commit()
    connection.close()
    return (ret)
