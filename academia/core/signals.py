from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Mark, Registration

@receiver(post_save, sender=Registration)
def create_mark(sender, instance, created, **kwargs):
    if created:
        Mark.objects.create(
            course = instance.course,
            student = instance.student,
            mark_1 = 0,
            mark_2 = 0,
            mark_3 = 0,
            average = 0
        )