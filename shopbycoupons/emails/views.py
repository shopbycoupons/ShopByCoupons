from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .models import Email
import smtplib
import ssl
import pymysql


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
    smtp.connect('email-smtp.us-east-1.amazonaws.com', 25)
    smtp.starttls()
    smtp.login('AKIAJ2YLI6QE5JRTSIWQ', 'AiePWord+xh9ui5nDSRRu8y5ril7SkOBCZ/mnSyuctsB')
    sender = 'crypto@bitcoinsnmore.com'
    receivers = 'aggarwal.anurag@gmail.com'
    message = """X-SES-MESSAGE-TAGS: tagName1=""" + tag1 + """, tagName2=""" + tag2 + """
X-SES-CONFIGURATION-SET: Track
From: "LetsDoc" <crypto@bitcoinsnmore.com>
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

def aws(request):
    content = list(request.POST.items())
    return HttpResponse(content)
