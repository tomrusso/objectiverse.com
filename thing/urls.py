from django.conf.urls import url, patterns

urlpatterns = patterns('thing.views',
	url(r'^tag$', 'tag'),
	url(r'^thing/(?P<thing_id>\d+)$', 'thing'),
	url(r'^thingpr\/(?P<private_id>\d+)\/(?P<scan_id>\d+)$', 'thing_private'),
	url(r'^create$', 'create_thing'),
	url(r'^scan$', 'scan'),
	url(r'^scan_update$', 'scan_update'),
	url(r'^search', 'search'),
	url(r'^maps$', 'map'),
	url(r'^coords', 'coords'),
)
