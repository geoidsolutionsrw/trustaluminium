import datetime
import logging

from django.utils.timezone import now
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware

logger = logging.getLogger(__name__)

class CustomSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        super().process_request(request)
        
        if request.session.get('last_activity'):
            last_activity = request.session.get('last_activity')
            elapsed_time = (now() - datetime.datetime.fromisoformat(last_activity)).total_seconds()

            if elapsed_time > settings.SESSION_COOKIE_AGE:
                logger.info(f"Session expired for user {request.user} at {now()}")
                request.session.flush()  # Log out user and delete session

        request.session['last_activity'] = now().isoformat()
