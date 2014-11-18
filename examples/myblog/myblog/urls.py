from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myblog.views.home', name='home'),
    url(r'^post/', include('post.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
