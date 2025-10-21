# --- Stage 1: Build dependencies ---
FROM python:3.10-slim-bullseye as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  gettext \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt ./requirements.txt


# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Run application ---
FROM python:3.10-slim-bullseye as application

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"

# Copy installed python dependencies
COPY --from=builder /opt/venv /opt/venv


# Copy entrypoint and start scripts
COPY ./compose/production/django/entrypoint /entrypoint
COPY ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /entrypoint /start \
  && chmod +x /entrypoint /start

# Copy the Django application from the context
COPY . .

# Use the start script as the entrypoint
ENTRYPOINT ["/entrypoint"]
