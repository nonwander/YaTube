from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()
per_page = settings.PER_PAGE


def index(request):
    post_list = Post.objects.select_related("group").order_by("-pub_date")
    paginator = Paginator(post_list, per_page)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "post_list": post_list,
        "paginator": paginator,
    }
    return render(request, "index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_list = group.posts.all()
    paginator = Paginator(group_list, per_page)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "group": group,
        "title": group.title,
        "description": group.description,
        "page": page,
        "post_list": group_list,
        "paginator": paginator,
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect("index")
    return render(request, "new_post.html", {"form": form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_posts = author.posts.all()
    paginator = Paginator(user_posts, 11)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    count = Post.objects.filter(author=author).select_related("author").count()
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author,
        ).exists()
    followers = Follow.objects.filter(author=author).count()
    follows = Follow.objects.filter(user=author).count()
    is_user = True
    if request.user == author:
        is_user = False
    context = {
        "page": page,
        "author": author,
        "count": count,
        "paginator": paginator,
        "following": following,
        "follows": follows,
        "followers": followers,
        "is_user": is_user,
    }
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    posts_count = post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        "post": post,
        "author": author,
        "count": posts_count,
        "form": form,
        "comments": comments,
    }
    return render(request, "post.html", context)


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post.author:
        return redirect(reverse("post", args=[post.author.username, post.id]))
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect(reverse("post", args=[post.author.username, post.id]))
    context = {
        "form": form,
        "post": post,
        "is_edit": True,
    }
    return render(request, "post_edit.html", context)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    context = {
        "post": post,
        "form": form,
    }
    if not form.is_valid():
        return render(request, "post.html", context)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    form.save()
    return redirect("post", username=username, post_id=post_id)


@login_required
def follow_index(request):
    authors = Follow.objects.filter(user=request.user)
    post_list = []
    for author in authors:
        post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator,
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author and not Follow.objects.filter(
        user=request.user, author=author
    ).exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("profile", username=username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404,
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
