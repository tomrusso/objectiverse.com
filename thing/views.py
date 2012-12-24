from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from thing.models import Tag, Thing, Scan, ThingForm, ScanForm
from django.template import RequestContext
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from random import randint

def empty(request): return HttpResponse("")

# The public view of a thing that anyone can access
def thing(request, thing_id):
	t = Thing.objects.get(pk=thing_id)
	return render_to_response("thing/thing.html", RequestContext(request, { 't': t, }))

# The private view of a thing which can only be accessed by those who scan the tag
def thing_private(request, private_id, scan_id):
	t = Tag.objects.get(private_id=private_id)
	sf = ScanForm()
	return render_to_response("thing/thing.html", RequestContext(request, { 't': t.thing, 'sf': sf, 'scan_id': scan_id }))

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
