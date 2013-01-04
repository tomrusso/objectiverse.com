from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from thing.models import Tag, Thing, Scan, ThingForm, ScanForm
from django.template import RequestContext
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from random import randint
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# The public view of a thing that anyone can access
def thing(request, thing_id):
	t = Thing.objects.get(pk=thing_id)
	# TODO: At some point should make things per page a constant, see thing_private view below 
	scans = paginate(t.scan_set.all().order_by("-timestamp"), 20, request)
	return render_to_response("thing/thing.html", RequestContext(request, { 't': t, 'scans': scans, }))

# The private view of a thing which can only be accessed by those who scan the tag
def thing_private(request, private_id, scan_id):
	t = Tag.objects.get(private_id=private_id)
	# TODO: At some point should make things per page a constant, see thing view above
	scans = paginate(t.scan_set.all().order_by("-timestamp"), 20, request)
	sf = ScanForm()
	return render_to_response("thing/thing.html", RequestContext(request, { 't': t.thing, 'sf': sf, 'scan_id': scan_id, 'scans': scans }))

# The view of things that gets displayed on the front page
def all(request):
	# Should update this to sort by recent activity
	recent_things = paginate(Thing.objects.all().order_by("-timestamp"), 20, request)
	return render_to_response("thing/all.html", RequestContext(request, { 'thing_set': recent_things, }))

# Search results view.
def search(request):
	query = request.REQUEST['query']
	things = paginate(Thing.objects.filter(description__contains=query), 20, request)

	return render_to_response("thing/search.html", RequestContext(request, { 'thing_set': things, 'query': query, }))

# Map view.  Either for an individual thing or for things with the most recent activity.
def map(request):
	if request.REQUEST.has_key('id'):
		t = Thing.objects.get(pk=int(request.REQUEST['id']))
		return render_to_response("thing/map.html", RequestContext(request, { 't': t, }))
	else:
		return render_to_response("thing/map.html", RequestContext(request, { }))

# Produce a JSON list that is returned to the maps page to populate the map.
def coords(request):
	if request.REQUEST.has_key('id'):
		scans = Scan.objects.filter	(	thing__pk=int(request.REQUEST['id']),
										latitude__isnull=False, 
										longitude__isnull=False
									).order_by("-timestamp")[:20]
	else:
		scans = Scan.objects.filter(latitude__isnull=False, longitude__isnull=False).order_by("-timestamp")[:20]

	# TODO: Think about whether to factor this out into a template.
	response = "["
	for scan in scans:
		response += "{ lat: %f, long: %f }, " % (scan.latitude, scan.longitude)
	response += "]"
	return HttpResponse(response)

# Get a paginated list of objects
def paginate(objects, num_per_page, request):
	paginator = Paginator(objects, num_per_page)

	page = request.GET.get('page')
	try:
		# Deliver the requested page
		paged_objects = paginator.page(page)
	except PageNotAnInteger:
		# If page is missing or not an integer, show the first page
		paged_objects = paginator.page(1)
	except EmptyPage:
		# If the page is out of range, show the last page
		paged_objects = paginator.page(paginator.num_pages)

	return paged_objects

# Tag creation view
def tag(request):
	tags = []
	for _ in range(0, 6):
		row = []
		for _ in range(0, 4):
			t = Tag()
			while True:
				t.private_id = randint(100000000, 999999999)
				try:
					t.save()
				except IntegrityError: continue
				break
				
			row.append(t)
		tags.append(row)

	return render_to_response("thing/tag.html", { 'tags': tags, })

# Thing creation view
def create_thing(request):
	private_id = None
	if request.method == "POST":
		t = Tag.objects.get(private_id=request.POST['private_id'])
		request.POST['tag'] = t.pk
		form = ThingForm(request.POST, request.FILES)
		if form.is_valid():
			th = form.save()
			if th:
				return HttpResponseRedirect("/thing/thing/%d" % th.pk)
			else:
				return HttpResponseRedirect("/error")
	else:
		if request.method == "GET" and request.GET.has_key("id"):
			private_id = request.GET["id"]
		form = ThingForm()
	return render_to_response('thing/create.html', { 'form': form, 'private_id': private_id, }, context_instance=RequestContext(request))

# Creates the page that grabs location from the browser and redirects to the appropriate
# URL to create a scan of the thing.
def location(request, thing_id):
	return render_to_response("thing/location.html", RequestContext(request, { 'thing_id': thing_id, }))

# Scan creation view -- calledd whenever a thing is scanned
def scan(request):
	t = Tag.objects.get(private_id=request.POST['id'])

	try:
		th = t.thing
	except ObjectDoesNotExist:
		return HttpResponseRedirect("/thing/create?id=%d" % int(request.POST['id']))

	sc = Scan()
	sc.thing = th
	sc.latitude = request.POST['lat']
	sc.longitude = request.POST['long']
	sc.save()

	return HttpResponseRedirect("/thing/thingpr/%d/%d" % (th.tag.private_id, sc.pk))

# Scan update view -- called when a user adds a comment and/or photo
def scan_update(request):
	sc = Scan.objects.get(pk=request.POST['scan_id'])
	sc.body = request.POST['body']
	if request.FILES.has_key('photo'):
		sc.photo = request.FILES['photo']
	sc.save()
	return HttpResponseRedirect("/thing/thing/%d" % sc.thing.tag.pk)
