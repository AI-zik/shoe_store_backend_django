import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ShoeImage


@receiver(post_delete, sender=ShoeImage)
def clear_images(sender, instance, **kwargs):
    if instance.medium:
        os.remove(instance.medium.path)
    if instance.thumbnail:
        os.remove(instance.thumbnail.path)
    if instance.image:
        os.remove(instance.image.path)


