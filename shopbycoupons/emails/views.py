from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .models import Email
import smtplib
import ssl
import json
import pymysql
from appconfig import *
from config import *
from django.views.decorators.csrf import csrf_exempt
import webbrowser
import urllib.request
import requests
from django.contrib.auth.decorators import login_required
from .tasks import send_email
from datetime import datetime

@login_required
def index(request):
    return render(request, 'emails/index.html')


def email(request):
    connection = pymysql.connect(host="localhost",user=proddbuser, passwd=proddbpass, database=proddbname )
    cursor = connection.cursor()

    content = list(request.POST.items())
    values = dict(content)
    tag1 = values["tag1"]
    tag2 = values["tag2"]
    emailsubject = values["emailsubject"]
    emailbody = values["emailbody"]
    estart = values["emailstart"]
    noemails = values["numberofemails"]

    cursor.execute("select email, status from email limit %s, %s", (int(estart), int(noemails)))
    emailsfromdb = (cursor.fetchall())
    listofemails = ['aggarwal.anurag@yahoo.com']

    for item in emailsfromdb:
        if item[1] =='Bounce' or item[1] == 'Complaint' or item[1] == 'Unsubscribe' or item[1] =='bounce':
            continue
        listofemails.append(item[0])

    listofemails = [x.strip() for x in listofemails]
    sent = len (listofemails)
    date = datetime.now()
    complaints = 0
    bounces = 0
    clicks = 0
    opens = 0
    unsubscribes = 0

    cursor.execute("insert into emails_campaign (id, tag1, tag2, sent, complaints, bounces, clicks, opens, unsubscribes) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (date, tag1, tag2, int(sent), int(complaints), int(bounces), int(clicks), int(opens), int(unsubscribes)))
    connection.commit()
    connection.close()



    smtp = smtplib.SMTP()
    smtp.connect(svcpvd, 25)
    smtp.starttls()
    smtp.login(smtp3, smtp4)
    for item in listofemails:
        sender = 'LetsDoc <alerts@shopbycoupons.in>'
        receivers = item
        url = "http://shopbycoupons.in/emails/unsubscribe/?email=" + item + "&tag1=" + tag1 + "&tag2=" + tag2
        message = """\
X-SES-MESSAGE-TAGS: tagName1="""+ tag1 +""", tagName2=""" + tag2+"""
X-SES-CONFIGURATION-SET: Track
From: LetsDoc <alerts@shopbycoupons.in>
To: """ + item +"""
Subject: """+ emailsubject +"""
Content-Type: multipart/alternative;
    boundary="----=_boundary"

------=_boundary
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 7bit

body
------=_boundary
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: 7bit

<table bgcolor="#c7c7c7" cellspacing="50" cellpadding="20">
  <tr bgcolor="#c7c7c7">
    <td style="background-color:#f4f4f4">
      <img src="https://letsdoc.in/assets/img/letsdoclogo2.png" width="200px"/><br/>
      <p style="font-size:100%">Healthcare Delivered Online</p>
      <br/>
      <p style="font-size:120%">
    """+ emailbody +"""
<br/><br/><br/>
<b>Regards<br/>
Team LetsDoc<br/></b>
Healthcare delivered online<br/>
In case of any queries, please reply to this mail.
<br/><br/>
<a href="""+ url +""">Click here to unsubscribe</a>
</p>
</td>
  </tr>

</table>

------=_boundary--
"""
        try:
            smtp.sendmail(sender, receivers, message)
        except (smtplib.SMTPDataError, smtplib.SMTPRecipientsRefused):
            continue

    printit = "Successfully sent email"
    smtp.quit()

    return HttpResponse(printit)

@csrf_exempt
def aws(request):
    a = json.loads(request.body.decode('utf-8'))
    m = request.META
    l = m['HTTP_X_AMZ_SNS_MESSAGE_ID']
    b= a['Type']
    c= a['Message']
    if b=='Notification':
        d = send_email.delay(l, c)
        return HttpResponse(d)
    elif b=='SubscriptionConfirmation' and a['TopicArn']== tarn:
        z = requests.get(a['SubscribeURL'])
        return HttpResponse(z)
    else:
        return HttpResponse('error')

def subscribe(request):
    content = list(request.POST.items())
    values = dict(content)
    name = values["name"]
    email = values["email"]

    smtp = smtplib.SMTP()
    smtp.connect(serviceprovider, 25)
    smtp.starttls()
    smtp.login(smtp1, smtp2)
    sender = 'aggarwal.anurag@gmail.com'
    receivers = email
    tag1 = 'sbc'
    tag2 = 'subscription'
    emailsubject = 'ShopByCoupons : Subscription Confirmation'
    emailbody = 'Thanks for Subscribing'
    message = """
X-SES-MESSAGE-TAGS: tagName1=""" + tag1 + """, tagName2=""" + tag2 + """
X-SES-CONFIGURATION-SET: Track
From: "ShopByCoupons" <aggarwal.anurag@gmail.com>
To: aggarwal.anurag@gmail.com
Subject: """ + emailsubject + """
Content-Type: multipart/alternative;
boundary="----=_boundary"

------=_boundary
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 7bit

body
------=_boundary
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: 7bit

""" + emailbody + """

------=_boundary--
"""

    smtp.sendmail(sender, receivers, message)
    printit = "Subscription confirmation email sent"
    smtp.quit()
    return HttpResponse(printit)

def unsubscribe(request):
    date = datetime.now()
    url = request.META.get('QUERY_STRING')
    urlstring = url.split("&")
    eid = urlstring[0][6:]
    tag1 = urlstring[1][5:]
    tag2 = urlstring[2][5:]
    status = 'Unsubscribe'
    connection = pymysql.connect(host="localhost",user=proddbuser, passwd=proddbpass, database=proddbname )
    cursor = connection.cursor()
    cursor.execute ("""\
        UPDATE email
        SET status=%s, date=%s
        WHERE email=%s
    """, (status, date, eid))

    cursor.execute("select unsubscribes from emails_campaign where tag1=%s and tag2=%s", (tag1, tag2))
    unsubscribe = cursor.fetchall()
    unsubscribes = unsubscribe[0][0]+1
    cursor.execute ("""\
        UPDATE emails_campaign
        SET unsubscribes=%s
        WHERE tag1=%s AND tag2=%s
    """, (int(unsubscribes), tag1, tag2))

    connection.commit()
    connection.close()
    return render(request, 'emails/unsubscribe.html')
