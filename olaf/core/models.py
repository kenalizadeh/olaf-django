from django.utils import timezone
import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.managers import BaseManager


class BaseModel(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    is_deleted = models.BooleanField(default=False)
    date_deleted = models.DateTimeField(blank=True, null=True, verbose_name=_("Deleted date"))
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated date"))
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created date"))

    objects = BaseManager()
    objects_including_deleted = BaseManager(include_deleted=True)

    def delete(self, using=None, keep_parents=False):
        if self.is_deleted: return

        self.date_deleted = timezone.now()
        self.is_deleted = True
        self.save()

    def restore(self):
        if not self.is_deleted: return

        self.date_deleted = None
        self.is_deleted = False
        self.save()

    def erase(self):
        super(BaseModel, self).delete()

    class Meta:
        abstract = True


class GeoPoint(models.Model):
    latitude = models.DecimalField("Latitude", max_digits=9, decimal_places=6)
    longitude = models.DecimalField("longitude", max_digits=9, decimal_places=6)

    class Meta:
        abstract = True


class Rating(models.Model):
    rating = models.IntegerField()

    class Meta:
        abstract = True
