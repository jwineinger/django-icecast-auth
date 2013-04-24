from datetime import datetime, timedelta

from django.db import models


class Mount(models.Model):
    name = models.CharField(max_length=20)
    
    def __unicode__(self):
        return unicode(self.name)


class Authorization(models.Model):
    """A model representing an authorization to access a specific mount"""
    mount = models.ForeignKey(Mount, related_name='authorizations')
    user = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    start = models.DateTimeField()
    end = models.DateTimeField()
    
    def __unicode__(self):
        return u"%s on %s" % (self.user, self.mount)


class Listener(models.Model):
    """
    A model representing a listener to a mount.  Instances of this model are
    only created after the listener is disconnected
    """
    mount = models.ForeignKey(Mount, related_name='listeners')
    user = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.IntegerField()
    
    def __unicode__(self):
        return u"%s on %s for %d seconds" % (self.user, self.mount, self.duration)


class AuthToken(models.Model):
    """
    Model to be used to store tokens generated in the HTTP Auth pre-stream
    view.  Then we redirect to the stream view with the username but the
    token as the password.  In the listener_add view, we look up the username
    and token to validate that they have indeed authed.
    """
    username = models.CharField(max_length=20)
    token = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.expires = datetime.utcnow() + timedelta(hours=1)
        return super(AuthToken, self).save(*args, **kwargs)