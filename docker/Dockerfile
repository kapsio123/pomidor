# build stage
FROM python:3.12-slim AS builder

WORKDIR /build
COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# runtime stage
FROM python:3.12-slim

# run as non-root user
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ .

USER appuser
EXPOSE 5000

ENV APP_VERSION=dev

HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# note: since I was using in memory session storage, I had to use a single worker.
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "1", "app:app"]