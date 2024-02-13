from django.core.cache import cache
from django.db import models


def delete_model_cache_for_current_user(prefix_cache: str, user_id: int) -> None:
    cache.delete(f"{prefix_cache}_{user_id}")


def get_calculate_standard_cache(user_id: int):
    cache_name = f"calculate_standard_{user_id}"
    standard_cache = cache.get(cache_name)
    return standard_cache


def get_calculate_current_cache(user_id: int):
    cache_name = f"calculate_current_{user_id}"
    current_cache = cache.get(cache_name)
    return current_cache


def get_or_set_model_cache(prefix_cache: str, user_id, model: models.Model, **kwargs):
    """
    Return found cache or create
    """
    cache_name = f"{prefix_cache}_{user_id}"
    get_cache = cache.get(cache_name)
    if get_cache:
        return get_cache
    else:
        queryset = model.objects.filter(**kwargs)
        cache.set(cache_name, queryset, 60 * 60 * 1)
        return queryset
