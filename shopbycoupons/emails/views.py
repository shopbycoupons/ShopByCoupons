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
from emails.models import *
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import Context, Template
from django.template.loader import get_template
from django.utils.html import strip_tags

@login_required
def index(request):
    return render(request, 'emails/index.html')


def email(request):
    content = list(request.POST.items())
    values = dict(content)
    user_base = values["user_base"]
    tag1 = values["tag1"]
    tag2 = values["tag2"]
    emailsubject = values["emailsubject"]
    emailbody = values["emailbody"]
    if user_base == "kg":
        estart = values["emailstart"]
        noemails = values["numberofemails"]
    elif user_base == "LetsDoc":
        ld_user = values["ld_user"]

    if user_base == "kg":
        emailsfromdb = email.objects.order_by('id')[estart:noemails]

    elif user_base == "LetsDoc":
        if ld_user =="All":
            emailsfromdb = letsdoc_users.objects.filter(source = 'LetsDoc')

        elif ld_user =="Users with points":
            emailsfromdb = letsdoc_users.objects.filter(source = 'LetsDoc', points__level__gt = 0)

        else:
            emailsfromdb = letsdoc_users.objects.filter(source = 'LetsDoc', points = 0)

    elif user_base == "Thyrocare Serviced":
        emailsfromdb = letsdoc_users.objects.filter(source = 'Thyrocare Serviced')

    elif user_base == "Thyrocare Not Serviced":
        emailsfromdb = letsdoc_users.objects.filter(source = 'Thyrocare Not Serviced')

    else:
        emailsfromdb = []

    listofemails = ['aggarwal.anurag@yahoo.com', 'aggarwal.anurag@gmail.com', 'anish.swaminathan@gmail.com']
    nameofuser = ['Anurag', 'Anurag Aggarwal', 'Anish']
    for item in emailsfromdb:
        if item.status =='Bounce' or item.status == 'Complaint' or item.status == 'Unsubscribe' or item.status =='bounce':
            continue
        listofemails.append(item.email)
        if user_base != "kg":
            nameofuser.append(item.name)

    listofemails = [x.strip() for x in listofemails]
    sent = len (listofemails)
    date = datetime.now()
    complaints = 0
    bounces = 0
    clicks = 0
    opens = 0
    unsubscribes = 0

    campaign_details = campaign (id = date, tag1 = tag1, tag2 = tag2, sent = sent, complaints = complaints, bounces = bounces, clicks = clicks, opens = opens, unsubscribes = unsubscribes)
    campaign_details.save()

    t1 = 'tagName1='+tag1
    t2 = 'tagName2='+tag2

    for counter, item in enumerate(listofemails):
        if user_base == "kg" or user_base == "kg Test":
            username = "Hi"
            sender = 'LetsDoc <alerts@shopbycoupons.in>'
        else:
            username = "Hi " + nameofuser[counter]
            sender = 'LetsDoc <support@letsdoc.in>'

        url = "http://shopbycoupons.in/emails/unsubscribe/?email=" + item + "&tag1=" + tag1 + "&tag2=" + tag2

        template = get_template("emails\\send_email.html")
        context = {'username':username, 'emailbody':emailbody, 'url':url}
        email_body = template.render(context)
        #email_body = render_to_string(template, context)
        text_email = strip_tags(email_body)
        email_send = EmailMultiAlternatives(emailsubject, text_email, sender, to=[item], headers={'X-SES-MESSAGE-TAGS': t1, 'X-SES-CONFIGURATION-SET': 'Track'})
        email_send.attach_alternative(email_body, "text/html")
        email_send.send()

    return HttpResponse(user_base)

@csrf_exempt
def aws(request):
    a = json.loads(request.body.decode('utf-8'))
    m = request.META
    l = m['HTTP_X_AMZ_SNS_MESSAGE_ID']
    b= a['Type']
    c= a['Message']
    if 'eventType' in c:
        if c['eventType'] != 'Delivery':
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
    if "kg" in tag1:
        cursor.execute("update email set status=%s, date=%s where email = %s", (status, date, eid))
    else:
        cursor.execute("update letsdoc_user set status=%s, date=%s where email = %s", (status, date, eid))

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
