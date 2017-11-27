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

from celery import Celery
from celery import shared_task
from celery import app

@shared_task
def send_email(sub,msg):
    #content = list(request.POST.items())
    #values = dict(content)
    tag1 = "tag1"
    tag2 = "tag2"
    emailsubject = sub
    emailbody = msg

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

    return (printit)
