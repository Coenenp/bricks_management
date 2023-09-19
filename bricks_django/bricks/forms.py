from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Part, Item, List, Color

class UserRegisterForm(UserCreationForm):
	email = forms.EmailField()

	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class PartForm(forms.ModelForm):
    item = forms.ModelChoiceField(queryset=Item.objects.all(), initial=0)
    color = forms.ModelChoiceField(queryset=Color.objects.all(), initial=0)
    list = forms.ModelChoiceField(queryset=List.objects.all(), initial=0)
    class Meta:
        model = Part
        fields = ['item', 'color', 'list']

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Select an Excel file')

