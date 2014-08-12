import base64, uuid
from datetime import timedelta, datetime


import requests
import django.utils.timezone
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect

from models import Authorization, Mount, Listener, AuthToken


def conregate_auth(username, password, mount):
    print "authing for %s, %s on '%s'" % (username, password, mount)
    try:
        now = django.utils.timezone.now()
        Authorization.objects.get(
            mount__name=mount,
            user=username,
            password=password,
            start__lte=now,
            end__gt=now,
        )
        print "found manual authorization"
        return True
    except Authorization.DoesNotExist:
        pass

    data = {
        'username': username,
        'password': password,
    }

    print "authing using congregate"
    resp = requests.post('https://nwcocmn.congregateclients.com/members/login', data, verify=False, allow_redirects=False)

    # success will issue a 302 redirect to the members home page
    if resp.status_code != 302:
        print "congregate auth failed"
        return False
    print "congregate auth success"
    return True


def basicauth_required(view):
    def wrap(request, *args, **kwargs):
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                if auth[0].lower() == "basic":
                    uname, passwd = base64.b64decode(auth[1]).split(':')
                    mount = kwargs['mount']
                    if conregate_auth(uname, passwd, mount):
                        return view(request, uname, mount)

        # Either they did not provide an authorization header or
        # something in the authorization attempt failed. Send a 401
        # back to them to ask them to authenticate.
        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="Northwest Church of Christ"'
        return response
    return wrap



@basicauth_required
def redirect_with_token(request, username, mount):
    token = AuthToken(
        username=username,
        token=uuid.uuid4(),
    )
    token.save()

    url = "http://%s:%s@%s/stream%s" % (
        username,
        token.token,
        request.get_host(),
        mount
    )
    return HttpResponseRedirect(url)


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
    token = request.POST[u'pass']

    try:
        print "lookup AuthToken: %s, %s" % (username, token)
        AuthToken.objects.get(
            username=username,
            token=token,
            expires__gte=datetime.utcnow(),
        )
        print "found it"
        r['icecast-auth-user'] = 1
        r['icecast-auth-message'] = '%s authorized' % request.POST[u'user']

    except AuthToken.DoesNotExist:
        print "token not found"
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
        mount=mount,
        start=start,
        end=end,
        duration=int(request.POST[u'duration'])
    )
    return HttpResponse()

