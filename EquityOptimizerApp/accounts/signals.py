import asyncio
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile


@receiver(post_save, sender=Profile)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        subject = "Welcome to Equity Optimizer App!"
        message = f"Hi {user.first_name},\n\nThank you for registering at Equity Optimizer App. We're excited to have you onboard!\n\nBest regards,\nThe Equity Optimizer Team"
        recipient_email = user.email

        asyncio.run(send_email_async(subject, message, recipient_email))


async def send_email_async(subject, message, recipient_email):

    loop = asyncio.get_event_loop()
    try:

        await loop.run_in_executor(
            None,
            send_mail,
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            False,
        )
        print(f"Welcome email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Failed to send welcome email to {recipient_email}: {e}")
