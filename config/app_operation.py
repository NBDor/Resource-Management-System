from config.settings import app_settings
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
import os
import sentry_sdk


def init_sentry():
    """
    This function initializes the Sentry SDK.
    """
    # TODO: add fast-lp-backend to sentry and fill the dsn here
    sentry_sdk.init(
        # dsn="https://20c62cbfdf88d4b1179e9da9297d8d2c@o4505798855557120.ingest.sentry.io/4506336389627904",
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        integrations=[
            StarletteIntegration(transaction_style="url"),
            FastApiIntegration(transaction_style="url"),
            CeleryIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )
