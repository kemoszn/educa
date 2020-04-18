from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module, Subject, Instructor

ModuleFormSet = inlineformset_factory(Course,
                                    Module,
                                    fields=['title',
                                            'description'],
                                    extra=2,
                                    can_delete=True)

class SubjectForm(forms.ModelForm):
        class Meta:
                model = Subject
                fields = ('title',)

class InstructorCreationForm(forms.ModelForm):
        class Meta:
                model = Instructor
                fields = ('name',)