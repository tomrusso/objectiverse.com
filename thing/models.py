from django.db import models
from django.forms import ModelForm, HiddenInput, Textarea

# Create your models here.
class Tag(models.Model):
	private_id = models.IntegerField(unique=True)

	def __unicode__(self):
		return "tag %s" % self.pk

class Thing(models.Model):
	# Things must have a tag.  TODO: Not sure about the primary_key=True part.
	tag = models.OneToOneField(Tag, primary_key=True)

	# Need to set MEDIA_ROOT I believe ...
	photo = models.ImageField(upload_to="photos")
	description = models.CharField(max_length=500)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "thing %s" % self.pk

class ThingForm(ModelForm):
	class Meta:
		model = Thing
		widgets = {
			'tag': HiddenInput(attrs={'value':'None',}),
		}

class Scan(models.Model):
	thing = models.ForeignKey(Thing)
	latitude = models.FloatField()
	longitude = models.FloatField()
	timestamp = models.DateTimeField(auto_now_add=True)
	body = models.CharField(max_length=500)
	user = models.EmailField()
	photo = models.ImageField(upload_to="photos")

class ScanForm(ModelForm):
	class Meta:
		model = Scan
		fields = {'body', 'user', 'photo', }
		widgets = {
			'body': Textarea(attrs={'cols':80, 'rows':5,}),
		}

class Comment(models.Model):
	# Every comment belongs to a thing.
	thing = models.ForeignKey(Thing)
	body = models.CharField(max_length=500)
	user = models.EmailField()

	def __unicode__(self):
		return "comment by " + self.user
