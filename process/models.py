from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone


class Snapshot(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    process_data = models.JSONField(encoder=DjangoJSONEncoder)

    def __str__(self):
        return f'Snapshot {self.id} by {self.author} at {self.timestamp}'

    class Meta:
        db_table = 'snapshot'