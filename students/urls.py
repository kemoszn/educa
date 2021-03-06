from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('register/',
        views.StudentRegistrationView.as_view(),
        name='student_registration'),
    path('courses/',
        views.StudentCourseListView.as_view(),
        name='student_course_list'),
    path('course/<pk>/',
        cache_page(60 * 15)(views.StudentModuleDetailView.as_view()),
        name='student_course_modules'),
    path('course/<pk>/<module_id>/',
        cache_page(60 * 15)(views.StudentCourseDetailView.as_view()),
        name='student_course_detail_module'),
]