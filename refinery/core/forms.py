'''
Created on Apr 15, 2012

@author: nils
'''

from django.forms import ModelForm, Textarea
from registration.forms import RegistrationFormUniqueEmail, RegistrationFormTermsOfService
from core.models import Project

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        exclude = ( "is_catch_all",)
        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 20}),
        }   
        
class RegistrationFormTermsOfServiceUniqueEmail(RegistrationFormTermsOfService, RegistrationFormUniqueEmail):
    pass 