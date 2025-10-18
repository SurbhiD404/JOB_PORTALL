from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings

token_generator = PasswordResetTokenGenerator()

def send_password_reset_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm/{uid}/{token}/"
    send_mail(
        subject="Password reset",
        message=f"Reset your password using this link: {reset_url}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
    )
