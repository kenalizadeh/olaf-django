from django.db import models

from user.models import User

class Notification(models.Model):
    title = models.CharField(max_length=256)
    message = models.TextField()
    read = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.user.phone_number + ' | ' + self.title
