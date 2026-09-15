from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect

from accounts.models import Profile
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.views import View

from blog.models import Post, Comment
from .forms import PostForm, CommentForm
from django.urls import reverse

# Create your views here.


class PostListView(ListView):
    context_object_name = "posts"
    template_name = "post_list.html"
    paginate_by = 2

    def get_queryset(self):
        return Post.objects.filter(
            status="True",
        ).order_by("created_at")


class PostDetailView(LoginRequiredMixin, View):
    template_name = "blog/post_detail.html"
    form_class = CommentForm

    def get(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)

        comments = (
            post.comments.select_related("author")
            .filter(parent=None)
            .order_by("created_at")
        )

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
        post = get_object_or_404(Post, pk=pk)

        action = request.POST.get("action")

        # CREATE / REPLY
        if action == "create":
            form = self.form_class(request.POST)

            if form.is_valid():
                comment = form.save(commit=False)

                comment.author = request.user.profile
                comment.post = post
                comment.name = comment.author.get_full_name()

                parent_id = request.POST.get("parent")

                if parent_id:
                    comment.parent = get_object_or_404(
                        Comment,
                        pk=parent_id,
                        post=post,
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
            )

            comment.delete()

            return redirect(
                reverse(
                    "blog:post-detail",
                    kwargs={"pk": pk},
                )
            )

        comments = (
            post.comments.select_related("author")
            .filter(parent=None)
            .order_by("created_at")
        )

        return render(
            request,
            self.template_name,
            {
                "post": post,
                "comments": comments,
                "form": form,
            },
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = "blog/post_create.html"
    model = Post

    form_class = PostForm
    success_url = reverse_lazy("blog:post-list")

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        form.instance.author = profile
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ["title", "content", "category"]
    template_name = "blog/post_update.html"
    success_url = reverse_lazy("blog:post-list")


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("blog:post-list")
    template_name = "blog/post_delete_confirm.html"
