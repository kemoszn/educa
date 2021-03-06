from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from .slug import unique_slugify
from django.utils.translation import gettext_lazy as _


class Subject(models.Model):
    title = models.CharField(_("title") ,max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
    
    def save(self, **kwargs):
        slug = '%s' % (self.title)
        unique_slugify(self, slug)
        super(Subject, self).save()

class Instructor(models.Model):
    name = models.CharField(_("name"),max_length=200, blank=False)

    def __str__(self):
        return self.name

class Course(models.Model):
    owner = models.ForeignKey(User,related_name='courses_created',
                            on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, verbose_name=_("subject"),
                            related_name='courses',
                            on_delete=models.CASCADE)
    title = models.CharField(_("title"),max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    instructor = models.ForeignKey(Instructor, 
                            related_name='instructor',
                            verbose_name=_("instructor"),
                            on_delete=models.CASCADE,
                            blank=True)
    overview = models.TextField(_("overview"))
    image = models.FileField(_("image"), upload_to="course_poster")
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User,
                                    related_name='courses_joined',
                                    verbose_name=_("students"),
                                    blank=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        slug = '%s' % (self.title)
        unique_slugify(self, slug)
        super(Course, self).save()

class Module(models.Model):
    course = models.ForeignKey(Course,
                        related_name='modules',
                        on_delete=models.CASCADE)
    title = models.CharField(_("title"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return '{}. {}'.format(self.order, self.title)
    

class Content(models.Model):
    module = models.ForeignKey(Module,
                        related_name='contents',
                        on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                        on_delete=models.CASCADE,
                        limit_choices_to={'model__in':(
                            'text','video','embedvideo','image','file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']


class ItemBase(models.Model):
    owner = models.ForeignKey(User,
                        related_name='%(class)s_related',
                        on_delete=models.CASCADE)
    title = models.CharField(_("title"), max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        return render_to_string('courses/content/{}.html'.format(
                            self._meta.model_name), {'item': self})

class Text(ItemBase):
    content = models.TextField(_("content"))

class File(ItemBase):
    file = models.FileField(_("file"), upload_to='files')

class Image(ItemBase):
    file = models.FileField(_("file"), upload_to='images')

class EmbedVideo(ItemBase):
    url = models.URLField(_("url"))

class Video(ItemBase):
    file = models.FileField(_("file"), upload_to='videos')