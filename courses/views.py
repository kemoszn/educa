from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet, SubjectCreationForm, InstructorCreationForm
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.db.models import Count
from .models import Subject
from django.views.generic.detail import DetailView
from django.core.cache import cache
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render_to_response
from django.core.paginator import Paginator

def superuser_required():
    def wrapper(wrapped):
        class WrappedClass(UserPassesTestMixin, wrapped):
            def test_func(self):
                return self.request.user.is_superuser

        return WrappedClass
    return wrapper

class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    model = Course
    fields = ['subject', 'instructor','title', 'students', 'overview']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    fields = ['subject', 'instructor','title', 'students', 'overview']
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/manage/course/form.html'

@superuser_required()
class ManageCourseListView(OwnerCourseMixin, LoginRequiredMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    paginate_by = 4

class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'

class CourseUpdateView(PermissionRequiredMixin, OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'

class CourseDeleteView(PermissionRequiredMixin, OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    success_url = reverse_lazy('manage_course_list')
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
                            data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super(CourseModuleUpdateView,
                    self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course,
                                        'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'embedvideo', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                'order',
                                                'created',
                                                'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)

        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                        id=id,
                                        owner=request.user)
        return super(ContentCreateUpdateView,
                    self).dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                            instance=self.obj,
                            data=request.POST,
                            files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module,
                item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form,
                                    'object': self.obj})

class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)

class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'
    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                id=module_id,
                                course__owner=request.user)
        return self.render_to_response({'module': module})

class ModuleOrderView(CsrfExemptMixin,
                    JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,
                                course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ContentOrderView(CsrfExemptMixin,
                    JsonRequestResponseMixin,
                    View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                         module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'
    def get(self, request, subject=None):
        subjects = cache.get('all_subjects')
        courses = Course.objects.all()
        if not subjects:
            subjects = Subject.objects.annotate(
                                            total_courses=Count('courses'))
            cache.set('all_subjects', subjects)
            courses = Course.objects.all()
            paginator = Paginator(courses, 6) 
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
        all_courses = Course.objects.annotate(
                                            total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = 'subject_{}_courses'.format(subject.id)
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
                cache.set('all_courses', courses)
                paginator = Paginator(courses, 6) 
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
            else:
                courses = cache.get('all_courses')
                if not courses:
                    courses = all_courses
                    cache.set('all_courses', courses)

        return self.render_to_response({'subjects': subjects,
                                        'subject': subject,
                                        'courses': courses,
                                        'page_obj': page_obj,
                                        'paginator': paginator})

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

@superuser_required()
class SubjectCreationView(CreateView):
    template_name = 'courses/course/new_subject.html'
    form_class = SubjectCreationForm
    success_url = reverse_lazy('manage_course_list')

    def form_valid(self, form):
        result = super(SubjectCreationView,
                    self).form_valid(form)
        return result

@superuser_required()
class InstructorCreationView(CreateView):
    template_name = 'courses/course/new_instructor.html'
    form_class = InstructorCreationForm
    success_url = reverse_lazy('manage_course_list')

    def form_valid(self, form):
        result = super(InstructorCreationView,
                    self).form_valid(form)
        return result

class SearchResultsView(ListView, View):
    model = Course
    template_name = 'courses/course/search_results.html'
    def get_queryset(self): 
        query = self.request.GET.get('q')
        object_list = Course.objects.filter(
            Q(title__icontains=query)
        )
        context = {'object_list': object_list, 'query':query}
        return context