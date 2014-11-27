from django.contrib.auth.models import User
from django import forms

class UserForm(forms.ModelForm):

  class Meta:
    #TODO: hide the password with correct widget

    model = User
    fields = ('username', 'email', 'password')
