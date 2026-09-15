from celery import shared_task
from mail_templated import EmailMessage
from accounts.models import User


@shared_task(
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_email_reset_password(token, user_id):
    user = User.objects.get(id=user_id)
    message = EmailMessage(
        template_name="email/reset_password_email.tpl",
        context={"token": token, "user": user},
        from_email="admin@gmail.com",
        to=[user.email],
    )
    message.send()


@shared_task(
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_email_resend_activation_email(token, user_id):
    user = User.objects.get(id=user_id)

    message = EmailMessage(
        "email/activation_email.tpl",
        {"token": token, "user": user},
        "admin@gmail.com",
        [user.email],
    )
    message.send()


@shared_task(
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_email_register_activation(token, user_id):
    user = User.objects.get(id=user_id)
    message = EmailMessage(
        "email/activation_email.tpl",
        {"token": token, "user": user},
        "admin@gmail.com",
        [user.email],
    )
    message.send()
