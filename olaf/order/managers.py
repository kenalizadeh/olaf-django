from django.db import models


class OrderQuerySet(models.QuerySet):

    def confirmed(self):
        from order.models import Order

        return self.filter(status=Order.STATUS.DELIVERED)

    def pending(self):

        from order.models import Order

        return self.filter(status=Order.STATUS.SENT)


class OrderManager(models.Manager):

    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def confirmed(self):
        return self.get_queryset().confirmed()

    def pending(self):
        return self.get_queryset().pending()
