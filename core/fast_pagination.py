import abc
import hashlib

from django.core.paginator import Paginator, Page
from django.core.cache import cache
from django.conf import settings
from django.db.models.query import QuerySet


class BaseFastPaginator(metaclass=abc.ABCMeta):
    TIMEOUT = getattr(settings, "FAST_PAGINATION_TIMEOUT", 3600)
    PREFIX = getattr(settings, "FAST_PAGINATION_PREFIX", "fastpagination")

    @abc.abstractmethod
    def count():
        raise NotImplementedError

    @abc.abstractmethod
    def page(self, number):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_page(self, *args, **kwargs):
        raise NotImplementedError


class FastQuerysetPaginator(Paginator, BaseFastPaginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        encoded_query = str(object_list.query).encode("utf-8")
        raw_query_key = str(hashlib.md5(encoded_query).hexdigest())
        self.cache_pks_key = f"{self.PREFIX}:pks:{raw_query_key}"
        self.cache_count_key = f"{self.PREFIX}:count:{raw_query_key}"

    @property
    def count(self):
        result = cache.get(self.cache_count_key)
        if result is None:
            result = self.object_list.count()
            cache.set(self.cache_count_key, result, timeout=self.TIMEOUT)
        return result

    @property
    def pks(self):
        result = cache.get(self.cache_pks_key)
        if result is None:
            result = list(self.object_list.values_list("pk", flat=True))
            cache.set(self.cache_pks_key, result, timeout=self.TIMEOUT)
        return result

    def page(self, number):
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        pks = self.pks[bottom:top]
        object_list = self.object_list.filter(pk__in=pks)
        return self._get_page(object_list, number, self)

    def _get_page(self, *args, **kwargs):
        return FastQuerysetPage(*args, **kwargs)


class FastObjectPaginator(BaseFastPaginator, Paginator):
    def __init__(
        self,
        object_list,
        per_page,
        orphans=0,
        allow_empty_first_page=True,
        cache_key=None,
    ):
        if cache_key is None:
            raise ValueError("You should provide cache_key" + "for your results")
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        self.cache_count_key = f"{self.PREFIX}:count:{cache_key}"

    def page(self, number):
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        object_list = self.object_list[bottom:top]
        return self._get_page(object_list, number, self)

    @property
    def count(self):
        result = cache.get(self.cache_count_key)
        if result is None:
            result = len(self.object_list)
            cache.set(self.cache_count_key, result, timeout=self.TIMEOUT)
        return result

    def _get_page(self, *args, **kwargs):
        return FastObjectPage(*args, **kwargs)


class FastPaginator:
    def __new__(cls, *args, **kwargs):
        object_list = args[0]
        if isinstance(object_list, QuerySet):
            return FastQuerysetPaginator(*args, **kwargs)
        return FastObjectPaginator(*args, **kwargs)


class FastQuerysetPage(Page):
    def __len__(self):
        return len(self.paginator.ids)


class FastObjectPage(Page):
    def __len__(self):
        return len(self.paginator.object_list)
