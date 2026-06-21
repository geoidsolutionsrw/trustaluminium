# Matches your local Python (3.13) on Debian bookworm
FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System libraries needed to BUILD pycairo and RUN WeasyPrint / PDF rendering.
# build-essential, pkg-config, python3-dev, libcairo2-dev -> let pycairo compile.
# libpango / libgdk-pixbuf / shared-mime-info / fonts -> needed by WeasyPrint at runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    python3-dev \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project
COPY . .

# Port is resolved inside gunicorn.conf.py (from the PORT env var), so the
# start command contains no $PORT and never depends on shell expansion.
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn trust_aluminium.wsgi -c gunicorn.conf.py"]
