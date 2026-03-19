from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from datetime import datetime, timedelta


class RememberMeMiddleware(MiddlewareMixin):
    """
    Middleware to handle "Remember me" functionality.
    If remember_me checkbox is checked, extends session expiry to 30 days.
    """

    def process_response(self, request, response):
        if request.method == 'POST' and 'remember_me' in request.POST:
            # Extend session to 30 days (in seconds)
            request.session.set_expiry(30 * 24 * 60 * 60)
        return response
