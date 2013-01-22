from django.db import models
from django.forms import ModelForm, HiddenInput, Textarea
from django.db.models.signals import post_save
from django.dispatch import receiver
import PIL
from PIL import Image
from tempfile import TemporaryFile
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile

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
	small = models.ImageField(upload_to="photos", blank=True, null=True)
	description = models.CharField(max_length=500)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "thing %s" % self.pk

# TODO: It might be better to do this by overriding the save method of Thing ...
@receiver(post_save, sender=Thing)
def thing_post_save(sender, created, instance, **kwargs):
	if not created: return
	photo_filename = instance.photo
	basewidth = 150
	img = Image.open(photo_filename)
	wpercent = basewidth / float(img.size[0])
	hsize = int(img.size[1] * wpercent)
	img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
	img_io = StringIO.StringIO()
	img.save(img_io, format='JPEG')
	img_file = InMemoryUploadedFile(img_io, None, 'foo.jpg', 'image/jpeg', img_io.len, None)
	instance.small = img_file
	instance.save()
	img_file.close()


class ThingForm(ModelForm):
	class Meta:
		model = Thing
		exclude = ('small')
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
