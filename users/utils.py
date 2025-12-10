from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from .tokens import account_activation_token

def send_activation_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    activation_link = f"{request.scheme}://{request.get_host()}/users/activate/{uid}/{token}/"

    subject = "Активация аккаунта Catalyst"
    message = render_to_string('users/activation_email.html', {
        'user': user,
        'activation_link': activation_link,
    })

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
