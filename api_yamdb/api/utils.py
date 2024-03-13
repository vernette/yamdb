from django.conf import settings
from django.core.mail import send_mail


def send_confirmation_code(user, confirmation_code):
    subject = 'Код подтверждения для доступа к YamDB'
    message = (
        f'Добрый день, {user.username}! \n'
        f'Ваш код подтверждения '
        f'для получения токена на YamDB: \n'
        f'{confirmation_code}'
    )
    user_email = user.email
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email]
    )
