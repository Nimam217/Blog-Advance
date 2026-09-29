from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_redis import get_redis_connection

from .models import Category, Post


@receiver([post_save, post_delete], sender=Post)
def delete_cache_after_change_post_list(sender, instance, **kwargs):
    redis = get_redis_connection("default")

    pattern_1 = "*:post_list:*"
    pattern_2 = "*:1:views.decorators.cache.*"
    # delete api post list cache
    for key in redis.scan_iter(match=pattern_1):
        redis.delete(key)
    # delete render post list cache
    for key in redis.scan_iter(match=pattern_2):
        redis.delete(key)


@receiver([post_save, post_delete], sender=Category)
def delete_cache_after_change_category(sender, instance, **kwargs):
    redis = get_redis_connection("default")

    pattern = "*:category_list:*"

    for key in redis.scan_iter(match=pattern):
        redis.delete(key)
