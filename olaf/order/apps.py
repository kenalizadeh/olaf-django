from django.apps import AppConfig


class OrderConfig(AppConfig):
    name = 'order'
    verbose_name = 'User Order'

    def ready(self):
        import order.signals