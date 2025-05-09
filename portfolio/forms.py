from django import forms
from .models import Evaluation

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['score']
        widgets = {
            'score': forms.RadioSelect(choices=[(i, f'{i}점') for i in range(1, 6)])
        }

from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description']
