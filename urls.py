from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    (r'^listener/add/$', views.listener_add),
    (r'^listener/remove/$', views.listener_remove),
)
