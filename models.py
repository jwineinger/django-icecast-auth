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
