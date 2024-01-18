from django.db.models.signals import pre_delete
from django.dispatch import receiver

from bood_app.models import Product, Eating


@receiver(pre_delete, sender=Product)
def set_delete_product(sender, instance, **kwargs) -> None:
    """
    Удаление микроэлементов и витаминов
    """
    if instance.vitamins:
        vitamins = instance.vitamins
        instance.vitamins = None
        instance.save()
        vitamins.delete()
    if instance.microelements:
        microelements = instance.microelements
        instance.microelements = None
        instance.save()
        microelements.delete()


@receiver(pre_delete, sender=Eating)
def set_delete_eating(sender, instance, **kwargs) -> None:
    """
    Удаление продуктов с весом и воды
    """
    if instance.product_weight:
        product_weight = instance.product_weight
        instance.product_weight = None
        instance.save()
        product_weight.delete()
    if instance.water:
        water = instance.water
        instance.water = None
        instance.save()
        water.delete()
