import stripe
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User)
def create_stripe_acct(sender, instance, created, **kwargs):
    if created:

        # creating stripe customer if new user is created
        customer = stripe.Customer.create(
            email = instance.email,
            name = f"{instance.first_name} {instance.other_name if instance.other_name else ''} {instance.last_name}",
            metadata = {
                "user_id" : instance.id
            },
            description = "customer created from shoe store django"
        )
        instance.stripe_customer_id = customer.id
        instance.save()
    else:
        stripe.Customer.modify(instance.stripe_customer_id, email = instance.email)
    
    if instance.user_type == 1:
        instance.is_staff = True
        instance.save()



@receiver(post_delete, sender=User)
def delete_stripe_acct(sender, instance, **kwargs):
    if instance.stripe_customer_id:
        stripe.Customer.delete(instance.stripe_customer_id)