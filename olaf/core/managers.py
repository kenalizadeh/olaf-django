from django.db import models
from django.db.models import QuerySet


class BaseQuerySet(QuerySet):

    def delete(self):
        for obj in self: obj.delete()

    def restore(self):
        for obj in self: obj.restore()

    def erase(self):
        for obj in self: obj.erase()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)


class BaseManager(models.Manager):

    def __init__(self, *args, **kwargs):
        self.include_deleted = kwargs.pop('include_deleted', False)
        super(BaseManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.include_deleted:
            return BaseQuerySet(self.model)
        return BaseQuerySet(self.model).filter(is_deleted=False)

    def delete(self):
        return self.get_queryset().delete()

    def restore(self):
        return self.get_queryset().restore()

    def erase(self):
        return self.get_queryset().erase()
