# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from wa.models import CustomUser

#class LanguageForm(forms.Form):


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )


class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    OPTIONS = (
        ("HIN", "Hindi"),
        ("ENG", "English"),
        ("KAN", "Kannada"),
        ("BEN", "Bengali"),
        )
    Languages = forms.MultipleChoiceField(widget = forms.SelectMultiple, choices=OPTIONS)
    def __init__(self, *args, **kargs):
        super(CustomUserCreationForm, self).__init__(*args, **kargs)
        del self.fields['username']

    class Meta:
        model = CustomUser
        fields = ("email","languages_known","first_name",'phoneNo')

class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(CustomUserChangeForm, self).__init__(*args, **kargs)
        del self.fields['username']

    class Meta:
        model = CustomUser