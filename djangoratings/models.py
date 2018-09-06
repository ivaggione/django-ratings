from datetime import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields
from django.contrib.auth.models import User

try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.now

from managers import VoteManager, SimilarUserManager


class Vote(models.Model):
    content_type = models.ForeignKey(ContentType, related_name="votes")
    object_id = models.PositiveIntegerField()
    key = models.CharField(max_length=32)
    score = models.IntegerField()
    user = models.ForeignKey(User, blank=True, null=True, related_name="votes")
    ip_address = models.GenericIPAddressField(null=True) if hasattr(models, "GenericIPAddressField") else models.IPAddressField(null=True)
    hashed_ip_address = models.CharField(null=True)
    cookie = models.CharField(max_length=32, blank=True, null=True)
    date_added = models.DateTimeField(default=now, editable=False)
    date_changed = models.DateTimeField(default=now, editable=False)
    objects = VoteManager()
    content_object = fields.GenericForeignKey()

    class Meta:
        unique_together = (('content_type', 'object_id', 'key', 'user', 'hashed_ip_address', 'cookie'))

    def __unicode__(self):
        return u"%s voted %s on %s" % (self.user_display, self.score, self.content_object)

    def save(self, *args, **kwargs):
        self.date_changed = now()
        super(Vote, self).save(*args, **kwargs)

    def user_display(self):
        if self.user:
            return "%s (%s)" % (self.user.username, self.hashed_ip_address)
        return self.hashed_ip_address
    user_display = property(user_display)


class Score(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    key  = models.CharField(max_length=32)
    score = models.IntegerField()
    votes = models.PositiveIntegerField()
    
    content_object = fields.GenericForeignKey()

    class Meta:
        unique_together = (('content_type', 'object_id', 'key'), )

    def __unicode__(self):
        return u"%s scored %s with %s votes" % (self.content_object, self.score, self.votes)


class SimilarUser(models.Model):
    from_user = models.ForeignKey(User, related_name="similar_users")
    to_user = models.ForeignKey(User, related_name="similar_users_from")
    agrees = models.PositiveIntegerField(default=0)
    disagrees = models.PositiveIntegerField(default=0)
    exclude = models.BooleanField(default=False)
    objects = SimilarUserManager()

    class Meta:
        unique_together = (('from_user', 'to_user'), )

    def __unicode__(self):
        print u"%s %s similar to %s" % (self.from_user, self.exclude and 'is not' or 'is', self.to_user)


class IgnoredObject(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey()

    class Meta:
        unique_together = (('content_type', 'object_id'), )

    def __unicode__(self):
        return self.content_object
