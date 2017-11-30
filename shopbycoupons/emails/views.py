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

    cursor.execute("select email from email limit %s, %s", (int(estart), int(noemails)))
    emailsfromdb = (cursor.fetchall())
    listofemails = []

    for item in emailsfromdb:
        listofemails.append(item[0])

    listofemails = [x.strip() for x in listofemails]


    smtp = smtplib.SMTP()
    smtp.connect(svcpvd, 25)
    smtp.starttls()
    smtp.login(smtp3, smtp4)
    for item in listofemails:
        sender = 'LetsDoc <alerts@shopbycoupons.in>'
        receivers = 'aggarwal.anurag@gmail.com'
        message = """X-SES-MESSAGE-TAGS: tagName1=KG, tagName2=1st100
    X-SES-CONFIGURATION-SET: Track
    From: alerts@shopbycoupons.in
    To: aggarwal.anurag@gmail.com
    Subject: Rs.875 only for complete health test
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
          <p style="font-size:120%">The comprehensive health test below Rs.900 is back. Now book the <a href="https://letsdoc.in/aarogyam_thyrocare_packages/LETSDOC-SPECIAL-OFFER/11?affiliate=campext1">LetsDoc Special Package</a> with 78 test parameters and pay only Rs.1750 for 2 people.<br/><br/>

          <b>The package includes tests for:</b><br/>
           Blood Sugar, Cholesterol, CBC, Liver Function, Kidney Function, Thyroid, Urine, and more ...<br/><br/>

          <a href="https://letsdoc.in/aarogyam_thyrocare_packages/LETSDOC-SPECIAL-OFFER/11?affiliate=campext1">Book now and get 78 parameters for Rs.875/person.</a>
          <br/>
          Also, get 100 cashback in the form of LetsDoc credits for bookings before 29th September 2017.
          <br/><br/><br/>
          Team LetsDoc<br/>
          Healthcare delivered online
          <br/><br/>
          In case of any queries, please reply to this mail.
          <br/><br/>
        </p>
        </td>
      </tr>
    </table>

    ------=_boundary--
        """
        smtp.sendmail(sender, receivers, message)

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
    return render(request, 'emails/unsubscribe.html')
