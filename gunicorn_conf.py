import os

name = os.getenv("GUNICORN_NAME", "polaris-fast-lp-backend")
workers = os.getenv("GUNICORN_WORKERS", 2)
threads = os.getenv("GUNICORN_THREADS", 4)
loglevel = os.getenv("LOG_LEVEL", "INFO")
limit_request_line = 0
bind = "0.0.0.0:8000"
worker_class = "uvicorn.workers.UvicornWorker"
accesslog = "-"
