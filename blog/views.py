from multiprocessing import context

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView

from blog.models import Post
from .forms import PostForm


# Create your views here.



class PostListView(ListView):
    context_object_name = 'posts'
    template_name = 'post_list.html'
    paginate_by = 2
    def get_queryset(self):
        return Post.objects.filter(status='True').order_by('created_at')


class PostDetailView(DetailView):
    template_name = 'blog/post_detail.html'

    def get_queryset(self):
        return Post.objects.filter(status='True')

class PostCreateView(CreateView):
    template_name = 'blog/post_create.html'
    model = Post

    form_class = PostForm
    success_url = reverse_lazy('blog:post-list')
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'category']
    template_name = 'blog/post_update.html'
    success_url = reverse_lazy('blog:post-list')

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:post-list')
    template_name = 'blog/post_delete_confirm.html'

