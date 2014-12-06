from django.shortcuts import render, get_object_or_404, get_list_or_404
from post.models import BlogPost, Comment

def latest(request):
  posts = BlogPost.objects.all()[0:5]
  for post in posts:
    print(post)
  return render(request, 'latest.html', {'latest': posts})

def show_blog_post(request, blog_post_id):
  blogpost = get_object_or_404(BlogPost, pk=blog_post_id)
  comments = Comment.objects.filter(post=blogpost)
  return render(request, 'detail.html', {
    'post': blogpost,
    'comments': comments
    })
