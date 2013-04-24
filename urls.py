from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
	url(r'^auth(?P<mount>.*)$', views.redirect_with_token, name='stream_auth'),
    url(r'^listener/add/$', views.listener_add, name='listener_add'),
    url(r'^listener/remove/$', views.listener_remove, name='listener_remove'),
)
