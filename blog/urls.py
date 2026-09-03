from django.urls import path, include


from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostDeleteView,
    PostUpdateView,
)

# urls

app_name = "blog"
urlpatterns = [
    path("post/", PostListView.as_view(), name="post-list"),
    path("post/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("post/create/", PostCreateView.as_view(), name="post-create"),
    path(
        "post/<int:pk>/delete/", PostDeleteView.as_view(), name="post-delete"
    ),
    path(
        "post/<int:pk>/update/", PostUpdateView.as_view(), name="post-update"
    ),
    path(
        "api/v1/",
        include(
            ("blog.api.v1.urls", "api_v1"),
            namespace="api_v1",
        ),
    ),
]
