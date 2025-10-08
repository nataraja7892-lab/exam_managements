from django import forms
from .models import Exam
from django import forms
from .models import Result
from register.models import Student
from exam1.models import Exam

from django import forms
from .models import Exam
from register.models import Student
from exam1.models import Exam

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['exam_title', 'course', 'year', 'num_subjects']

    def __init__(self, *args, **kwargs):
        self.num_subjects = kwargs.pop('num_subjects', 0)
        super().__init__(*args, **kwargs)

        # Add dynamic fields for subjects, dates, and max marks
        for i in range(1, self.num_subjects + 1):
            self.fields[f'subject_{i}'] = forms.CharField(
                label=f'Subject {i} Name',
                required=True
            )
            self.fields[f'date_{i}'] = forms.DateField(
                label=f'Subject {i} Date',
                widget=forms.DateInput(attrs={'type': 'date'}),
                required=True
            )
            self.fields[f'max_marks_{i}'] = forms.IntegerField(
                label=f'Subject {i} Max Marks',
                min_value=1,
                required=True
            )

    def save(self, commit=True):
        exam = super().save(commit=False)
        subject_names = []
        subject_max_marks = []

        # Extract subject data from form
        for i in range(1, self.num_subjects + 1):
            subject_name = self.cleaned_data.get(f'subject_{i}')
            subject_date = self.cleaned_data.get(f'date_{i}')
            max_marks = self.cleaned_data.get(f'max_marks_{i}')

            subject_names.append({
                'name': subject_name,
                'date': subject_date.strftime('%Y-%m-%d')  # Format date as string
            })

            subject_max_marks.append({
                'name': subject_name,
                'max_marks': max_marks
            })

        # Assign to model fields
        exam.subject_names = subject_names
        exam.subject_max_marks = subject_max_marks

        if commit:
            exam.save()  # This triggers the post_save signal for total_max_marks

        return exam



from django import forms
from .models import Result, Exam, Student

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['exam', 'student', 'subject_marks']
    
    def __init__(self, *args, **kwargs):
        exam_id = kwargs.pop('exam_id', None)
        course = kwargs.pop('course', None)
        year = kwargs.pop('year', None)
        super().__init__(*args, **kwargs)
        
        if exam_id:
            exam = Exam.objects.get(id=exam_id)
            self.fields['subject_marks'] = forms.JSONField(
                widget=forms.widgets.Textarea(attrs={'rows': 5, 'cols': 50}),
                initial={f"subject_{i+1}": "" for i in range(exam.num_subjects)}
            )
        
        # Filter students based on course and year
        if course and year:
            self.fields['student'] = forms.ModelChoiceField(
                queryset=Student.objects.filter(course=course, year=year),
                empty_label="Select Student"
            )

        # Filter students based on course and year
        if course and year:
            self.fields['student'] = forms.ModelChoiceField(
                queryset=Student.objects.filter(course=course, year=year),
                empty_label="Select Student"
            )
