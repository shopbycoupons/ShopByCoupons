from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .models import Email
import smtplib
import ssl
import json
import pymysql
from appconfig import *
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
    content = list(request.POST.items())
    values = dict(content)
    tag1 = values["tag1"]
    tag2 = values["tag2"]
    emailsubject = values["emailsubject"]
    emailbody = values["emailbody"]

    smtp = smtplib.SMTP()
    smtp.connect(serviceprovider, 25)
    smtp.starttls()
    smtp.login(smtp1, smtp2)
    sender = 'aggarwal.anurag@gmail.com'
    receivers = 'aggarwal.anurag@gmail.com'
    message = """X-SES-MESSAGE-TAGS: tagName1=""" + tag1 + """, tagName2=""" + tag2 + """
X-SES-CONFIGURATION-SET: Track
From: "LetsDoc" <aggarwal.anurag@gmail.com>
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
    printit = "Successfully sent email"
    smtp.quit()

    return HttpResponse(printit)

@csrf_exempt
def aws(request):
    a = json.loads(request.body.decode('utf-8'))
    b= a['Type']
    c= a['Message']
    d=send_email.delay()
    return HttpResponse(b.decode())
