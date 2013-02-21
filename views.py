from datetime import timedelta

import requests
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import django.utils.timezone

from models import Authorization, Mount, Listener


class CongregateAuthFailure(Exception): pass

@csrf_exempt
def listener_add(request):
    """
    <QueryDict: {
        u'ip': [u'321.321.312.321'],
        u'mount': [u'/auth_test'],
        u'agent': [u'vlc/1.1.4 LibVLC/1.1.4'],
        u'server': [u'domain.tld'],
        u'client': [u'26'],
        u'user': [u''],
        u'pass': [u''],
        u'action': [u'listener_add'],
        u'port': [u'8888'],
    }>
    """
    r = HttpResponse()
    username = request.POST[u'user']
    password = request.POST[u'pass']

    try:
        now = django.utils.timezone.now()
        auth = Authorization.objects.get(
            mount__name=request.POST[u'mount'],
            user=username,
            password=password,
            start__lte=now,
            end__gt=now,
        )
        r['icecast-auth-user'] = 1
        r['icecast-auth-message'] = '%s authorized' % request.POST[u'user']
        r['icecast-auth-timelimit'] = int((auth.end - now).total_seconds())

    except Authorization.DoesNotExist:
        try:
            data = {
                'username': username,
                'password': password,
            }

            resp = requests.post('https://nwcocmn.congregateclients.com/members/login', data, verify=False, allow_redirects=False)

            # success will issue a 302 redirect to the members home page
            if resp.status_code != 302:
                raise CongregateAuthFailure

            r['icecast-auth-user'] = 1
            r['icecast-auth-message'] = '%s authorized' % username

        except CongregateAuthFailure:
            r['icecast-auth-message'] = "User not authorized"

    return r

@csrf_exempt
def listener_remove(request):
    """
    <QueryDict: {
        u'mount': [u'/auth_test'],
        u'server': [u'domain.tld'],
        u'duration': [u'20'],
        u'client': [u'58'],
        u'user': [u'jay'],
        u'pass': [u'jay'],
        u'action': [u'listener_remove'],
        u'port': [u'8888'],
    }>
    """
    end = django.utils.timezone.now()
    start = end - timedelta(seconds=int(request.POST[u'duration']))

    mount = get_object_or_404(Mount, name=request.POST[u'mount'])
    Listener.objects.create(
        user=request.POST[u'user'],
        password=request.POST[u'pass'],
        mount=mount,
        start=start,
        end=end,
        duration=int(request.POST[u'duration'])
    )
    return HttpResponse()
