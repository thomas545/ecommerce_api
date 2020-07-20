from django.db.models.signals import ModelSignal
from django.dispatch import Signal


signal = Signal(providing_args=["instance"], use_caching=True)


def post_signal(sender, instance):
    signal.send(sender=sender, instance=instance)
    print(sender, instance)
