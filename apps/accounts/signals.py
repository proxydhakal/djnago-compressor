from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.models import EmailAddress
from apps.accounts.models import UserAccount
from allauth.account.signals import email_confirmed

@receiver(post_save, sender=UserAccount)
def create_email_address(sender, instance, created, **kwargs):
    if instance.is_superuser:
        # Check if an EmailAddress with the same email already exists
        existing_email_address = EmailAddress.objects.filter(email=instance.email).first()

        if not existing_email_address:
            # If no matching EmailAddress found, create one
            email_address = EmailAddress.objects.create(
                user=instance,
                email=instance.email,
                verified=True,
                primary=True
            )
            email_address.save()

@receiver(email_confirmed)
def email_confirmed_handler(sender, request, email_address, **kwargs):
    # Get the user associated with the email address
    user = email_address.user
    # Update the UserAccount's status to ACTIVE
    user.is_email_verified = True
    user.save()