import os

# Railway ALWAYS injects and routes port 8080 at runtime, so we bind to it
# directly. Hardcoding avoids any dependency on shell variable expansion,
# which is the cause of the "'$PORT' is not a valid port number" error.
bind = "0.0.0.0:8080"
workers = 3
