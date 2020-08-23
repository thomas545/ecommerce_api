import socket
import datetime
from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS, caches, cache
from django.utils.cache import (
    get_cache_key,
    get_max_age,
    has_vary_header,
    learn_cache_key,
    patch_response_headers,
)
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User


class ActiveUserMiddleware(MiddlewareMixin):
    """
    Using Caching & Middlewares to Track Online Users
    """

    def process_request(self, request):
        if request.user.is_authenticated:
            now = datetime.datetime.now(datetime.timezone.utc)
            cache.set(
                f"seen_{request.user.username}", now, settings.USER_LASTSEEN_TIMEOUT
            )
        return None


class GooglebotMiddleware(object):
    """
    Middleware to automatically log in the Googlebot with the user account 'googlebot'
    """

    def process_request(self, request):
        request.is_googlebot = False  # Assume false, until proven
        if request.user == AnonymousUser():
            if request.META.get("HTTP_USER_AGENT"):
                if "Googlebot" in request.META["HTTP_USER_AGENT"]:
                    try:
                        remote_ip = request.META["REMOTE_ADDR"]
                        hostname = socket.gethostbyaddr(remote_ip)[0]

                        if hostname.endswith("googlebot.com"):
                            request.user, created = User.objects.get_or_create(
                                username="googlebot"
                            )  # login our googlebot user :)
                            request.is_googlebot = True
                        else:
                            # FAKE googlebot!!!!
                            request.is_googlebot = False

                    except Exception:
                        pass  # Don't bring down the site
        return None


class UpdateCacheMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.cache_alias = settings.CACHE_MIDDLEWARE_ALIAS
        self.cache = caches[self.cache_alias]
        self.get_response = get_response

    def _should_update_cache(self, request, response):
        return hasattr(request, "_cache_update_cache") and request._cache_update_cache

    def process_response(self, request, response):
        """Set the cache, if needed."""
        if not self._should_update_cache(request, response):
            # We don't need to update the cache, just return.
            return response

        if response.streaming or response.status_code not in (200, 304):
            return response

        # Don't cache responses that set a user-specific (and maybe security
        # sensitive) cookie in response to a cookie-less request.
        if (
            not request.COOKIES
            and response.cookies
            and has_vary_header(response, "Cookie")
        ):
            return response

        # Try to get the timeout from the "max-age" section of the "Cache-
        # Control" header before reverting to using the default cache_timeout
        # length.
        timeout = get_max_age(response)
        if timeout is None:
            timeout = self.cache_timeout
        elif timeout == 0:
            # max-age was set to 0, don't bother caching.
            return response
        patch_response_headers(response, timeout)
        if timeout and response.status_code == 200:
            cache_key = learn_cache_key(
                request, response, timeout, self.key_prefix, cache=self.cache
            )
            if hasattr(response, "render") and callable(response.render):
                response.add_post_render_callback(
                    lambda r: self.cache.set(cache_key, r, timeout)
                )
            else:
                self.cache.set(cache_key, response, timeout)
        return response


class FetchFromCacheMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.cache_alias = settings.CACHE_MIDDLEWARE_ALIAS
        self.cache = caches[self.cache_alias]
        self.get_response = get_response

    def process_request(self, request):

        if request.method not in ("GET", "HEAD"):
            request._cache_update_cache = True
            return None  # Don't bother checking the cache.

        # try and get the cached GET response
        cache_key = get_cache_key(request, self.key_prefix, "GET", cache=self.cache)
        if cache_key is None:
            request._cache_update_cache = True
            return None  # No cache information available, need to rebuild.
        response = self.cache.get(cache_key)
        # if it wasn't found and we are looking for a HEAD, try looking just for that
        if response is None and request.method == "HEAD":
            cache_key = get_cache_key(
                request, self.key_prefix, "HEAD", cache=self.cache
            )
            response = self.cache.get(cache_key)

        if response is None:
            request._cache_update_cache = True
            return None  # No cache information available, need to rebuild.

        # hit, return cached response
        request._cache_update_cache = True
        return response
