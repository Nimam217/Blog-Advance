from .views import (
    PostModelViewSet,
    CategoryModelViewSet,
    CommentModelViewSet,
)
from rest_framework.routers import DefaultRouter

app_name = "api_v1"


router = DefaultRouter()
router.register("post", PostModelViewSet, basename="post")
router.register("category", CategoryModelViewSet, basename="category")
router.register(
    "comment",
    CommentModelViewSet,
    basename="comment-api",
)
urlpatterns = router.urls
