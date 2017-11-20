from django.conf.urls import url

from . import views

app_name = 'emails'

urlpatterns = [url(r'^$', views.index, name='index'),
url(r'^/email/$', views.email, name='email'),
url(r'^/aws/$', views.aws, name='aws')]
