from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_redis import get_redis_connection

from .models import Category, Post


@receiver([post_save, post_delete], sender=Post)
def delete_cache_after_change_post_list(sender, instance, **kwargs):
    redis = get_redis_connection("default")

    pattern = "*:post_list:*"

    for key in redis.scan_iter(match=pattern):
        print("DELETING:", key)
        redis.delete(key)


@receiver([post_save, post_delete], sender=Category)
def delete_cache_after_change_category(sender, instance, **kwargs):
    redis = get_redis_connection("default")

    pattern = "*:category_list:*"

    for key in redis.scan_iter(match=pattern):
        redis.delete(key)
