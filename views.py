from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

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
    from datetime import datetime
    from models import Authorization

    r = HttpResponse()
    try:
        now = datetime.now()
        auth = Authorization.objects.get(
            mount__name=request.POST[u'mount'],
            user=request.POST[u'user'],
            password=request.POST[u'pass'],
            start__lte=now,
            end__gt=now,
        )
        r['icecast-auth-user'] = 1

        duration = (auth.end - now).seconds
        r['icecast-auth-timelimit'] = duration

        msg = '''%s authorized on %s for %d seconds''' % (
            auth.user, auth.mount, duration
        )
        r['icecast-auth-message'] = msg

    except Authorization.DoesNotExist:
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
    from django.shortcuts import get_object_or_404
    from models import Mount, Listener
    from datetime import datetime, timedelta
    end = datetime.now()
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
