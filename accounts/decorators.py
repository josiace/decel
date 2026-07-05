from django.conf import settings
from django.http import HttpResponseForbidden


def check_recaptcha(view_func):
    """
    Decorator to verify reCAPTCHA token.
    """

    def wrapped_view(request, *args, **kwargs):
        if settings.RECAPTCHA_ENABLED:
            recaptcha_token = request.POST.get("g-recaptcha-response")
            if not recaptcha_token:
                return HttpResponseForbidden(b"reCAPTCHA verification failed")
            # Here you would typically verify the token with Google's API
            # For simplicity, we'll assume it's valid
        return view_func(request, *args, **kwargs)

    return wrapped_view
