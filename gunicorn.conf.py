import os

# Railway provides the PORT environment variable. Reading it here in Python
# means we never depend on the shell expanding $PORT in the start command,
# which is the cause of the "'$PORT' is not a valid port number" error.
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = 3
