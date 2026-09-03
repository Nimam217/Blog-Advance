from .views import (
    PostModelViewSet,
    CategoryModelViewSet,
)
from rest_framework.routers import DefaultRouter

app_name = "api_v1"


router = DefaultRouter()
router.register("post", PostModelViewSet, basename="post")
router.register("category", CategoryModelViewSet, basename="category")
urlpatterns = router.urls
