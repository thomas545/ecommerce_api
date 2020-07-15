from django.db.models.signals import ModelSignal
from django.dispatch import Signal


class CustomSignal(ModelSignal):
    pass


register_signal = Signal(providing_args=["request", "user"])
