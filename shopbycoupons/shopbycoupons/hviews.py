import requests
import urllib.request
from django.shortcuts import render


def abc(request):
    return render(request, 'abc.html')
