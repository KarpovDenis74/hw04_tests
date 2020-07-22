from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.paginator import Paginator
from .models import Post, Group, User
from .forms import PostForm


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/profile.html',
        {'author': author, 'page': page, 'paginator': paginator})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    count = Post.objects.filter(author__username=username).count
    return render(request, 'posts/post.html',
        {'author': author, 'count': count, 'post': post}
    )


@login_required
def new_post(request):
    context = {'title': 'Новая запись', 'botton': 'Добавить'}
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'posts/new_post.html',
            {'context': context, 'form': form}
        )
    form = PostForm(request.POST)
    if not form.is_valid():
        return render(request,
            'posts/new_post.html', {'context': context, 'form': form}
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != post.author:
        return redirect('post', username=post.author.username, post_id=post_id)
    context = {'title': 'Редактировать запись',
        'botton': 'Сохранить',
        'post_id': post.id
    }
    form = PostForm(request.POST or None, instance=post)
    if not form.is_valid():
        return render(request, 'posts/new_post.html',
            {'post': post, 'context': context, 'form': form}
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect(f'/{post.author.username}/{post.id}')


def index(request):
    post_list = Post.objects.select_related('group').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.post_group.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html",
        {'group': group, 'page': page, 'paginator': paginator}
    )
