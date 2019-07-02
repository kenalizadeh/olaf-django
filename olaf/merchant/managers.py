from django.db import models


class MenuItemQuerySet(models.QuerySet):

    def active(self):
        return self.filter(active=True)

    def recommended(self):
        return self.filter(active=True, recommended=True)


class MenuItemManager(models.Manager):

    def get_queryset(self):
        return MenuItemQuerySet(self.model, using=self._db).active()


class RecommendedMenuItemManager(models.Manager):

    def get_queryset(self):
        return MenuItemQuerySet(self.model, using=self._db).recommended()
