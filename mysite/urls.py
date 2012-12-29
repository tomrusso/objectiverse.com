from django.conf.urls import patterns, include, url
import django.views.static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^thing/', include('thing.urls')),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^photos/(?P<path>.*)$', django.views.static.serve, { 'document_root': '/Users/tom/Documents/code/django/mysite/photos', }),
	url(r'^(?P<thing_id>\d+)$', 'thing.views.location'),
	url(r'^$', 'thing.views.all'),
)

#urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

#	url(r'^polls/$', 'polls.views.index'),
#	url(r'^polls/(?P<poll_id>\d+)/$', 'polls.views.detail'),
#	url(r'^polls/(?P<poll_id>\d+)/results/$', 'polls.views.results'),
#	url(r'^polls/(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),
    # Uncomment the next line to enable the admin:
#	url(r'^admin/', include(admin.site.urls)),
#)
