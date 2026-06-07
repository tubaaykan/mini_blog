import functools
import logging

from flask import flash, redirect, request


logger = logging.getLogger(__name__)


def handle_route_errors(default_endpoint: str = "main.index"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                logger.exception("Unexpected route failure in %s", func.__name__)
                flash("An unexpected error occurred. Please try again.", "danger")
                if request.referrer:
                    return redirect(request.referrer)
                from flask import url_for

                return redirect(url_for(default_endpoint))

        return wrapper

    return decorator
