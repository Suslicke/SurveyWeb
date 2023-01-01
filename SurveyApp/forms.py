from django import forms
from django.forms import CheckboxInput

from .models import *

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ["title"]
        
        
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["prompt"]
        
        
class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ["text", "is_right"]
        
        widget = {"is_right": CheckboxInput(attrs={'class': 'is_right'})}
        
        

class AnswerForm(forms.Form):
    submission_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    question_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    
    def __init__(self, submission_id, question_id, *args, **kwargs):
        
        options = kwargs.pop("options")
        # Options must be a list of Option objects
        choices = {(o.pk, o.text) for o in options}
        super().__init__(*args, **kwargs)
        option_field = forms.ChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple(), required=True)
        self.fields["option"] = option_field
        
        self.initial['submission_id'] = submission_id
        self.initial['question_id'] = question_id

        
        
# class BaseAnswerFormSet(forms.BaseFormSet):
#     def get_form_kwargs(self, index):
#         kwargs = super().get_form_kwargs(index)
#         kwargs["options"] = kwargs["options"][index]
#         return kwargs
