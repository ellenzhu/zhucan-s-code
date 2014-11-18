from django.conf.urls import patterns, include, url
from post.views import latest, show_blog_post

urlpatterns = patterns('',
    url(r'^latest$', latest, name='latest_posts'),
    url(r'^detail/(\d+)/$', show_blog_post, name='detail'),
)
