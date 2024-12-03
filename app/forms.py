"""
Implements the forms to Customer and Order models.
"""

# Django imports.
from django import forms

# Project imports.
from app.models import Customer


class CustomerForm(forms.ModelForm):

    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=100)

    class Meta:
        GENDER_CHOICES = (
            ('F', 'Female'),
            ('M', 'Male'),
        )

        model = Customer
        fields = ['first_name', 'last_name', 'document_id', 'gender', 'birthdate', 'email', 'phone', 'address']
        labels = {'first_name': 'First name',
                  'last_name': 'Last name',
                  'document_id': 'Document id',
                  'gender': 'Gender',
                  'birthdate': 'Date of birth',
                  'email': 'Email',
                  'phone': 'Phone number',
                  'address': 'Address'}
        widgets = {'gender': forms.Select(choices=GENDER_CHOICES),
                   'birthdate': forms.DateInput(attrs={'type': 'date', 'format': '%Y-%m-%d'}),
                   'address': forms.Textarea()}


