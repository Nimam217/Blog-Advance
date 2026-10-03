from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.views import View

from blog.models import Post, Comment
from .forms import PostForm, CommentForm


# Post List
@method_decorator(cache_page(timeout=60 * 20), name="dispatch")
class PostListView(ListView):
    context_object_name = "posts"
    template_name = "blog/post_list.html"
    paginate_by = 2

    def get_queryset(self):
        return Post.objects.filter(
            status=True,
        ).order_by("created_at")


# Post Detail + Comments
class PostDetailView(LoginRequiredMixin, View):
    template_name = "blog/post_detail.html"
    form_class = CommentForm

    def get_comments(self, post):
        return (
            post.comments.filter(
                parent=None,
                status=True,
            )
            .select_related("author")
            .prefetch_related(
                Prefetch(
                    "replies",
                    queryset=Comment.objects.filter(
                        status=True,
                    )
                    .select_related("author")
                    .order_by("created_at"),
                )
            )
            .order_by("created_at")
        )

    def get(self, request, pk, *args, **kwargs):
        post = get_object_or_404(
            Post,
            pk=pk,
            status=True,
        )

        comments = self.get_comments(post)

        form = self.form_class()

        return render(
            request,
            self.template_name,
            {
                "post": post,
                "comments": comments,
                "form": form,
            },
        )

    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(
            Post,
            pk=pk,
            status=True,
        )

        action = request.POST.get("action")

        # CREATE COMMENT / REPLY
        if action == "create":
            form = self.form_class(request.POST)

            if form.is_valid():
                comment = form.save(commit=False)

                comment.author = request.user.profile
                comment.post = post
                parent_id = request.POST.get("parent")

                if parent_id:
                    comment.parent = get_object_or_404(
                        Comment,
                        pk=parent_id,
                        post=post,
                        parent=None,
                        status=True,
                    )

                comment.save()

                return redirect(
                    reverse(
                        "blog:post-detail",
                        kwargs={"pk": pk},
                    )
                )

        # UPDATE
        elif action == "update":
            comment = get_object_or_404(
                Comment,
                pk=request.POST.get("comment_id"),
                author=request.user.profile,
                post=post,
                status=True,
            )

            form = self.form_class(
                request.POST,
                instance=comment,
            )

            if form.is_valid():
                form.save()

                return redirect(
                    reverse(
                        "blog:post-detail",
                        kwargs={"pk": pk},
                    )
                )

        # DELETE
        elif action == "delete":
            comment = get_object_or_404(
                Comment,
                pk=request.POST.get("comment_id"),
                author=request.user.profile,
                post=post,
                status=True,
            )

            comment.delete()

            return redirect(
                reverse(
                    "blog:post-detail",
                    kwargs={"pk": pk},
                )
            )

        comments = self.get_comments(post)

        return render(
            request,
            self.template_name,
            {
                "post": post,
                "comments": comments,
                "form": form,
            },
        )


# Post Create
class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = "blog/post_create.html"
    model = Post
    form_class = PostForm
    success_url = reverse_lazy("blog:post-list")

    def form_valid(self, form):
        form.instance.author = self.request.user.profile

        return super().form_valid(form)


# Post Update
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ["title", "content", "category"]
    template_name = "blog/post_update.html"
    success_url = reverse_lazy("blog:post-list")


# Post Delete
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("blog:post-list")
    template_name = "blog/post_delete_confirm.html"
