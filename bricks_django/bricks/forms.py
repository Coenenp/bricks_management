from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Part, Item, List, Color, ListPart
class UserRegisterForm(UserCreationForm):
	email = forms.EmailField()

	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class PartForm(forms.ModelForm):
    item = forms.ModelChoiceField(queryset=Item.objects.all(), empty_label=None, required=True)
    color = forms.ModelChoiceField(queryset=Color.objects.all(), empty_label=None, required=True)
    list = forms.ModelChoiceField(queryset=List.objects.all(), empty_label=None, required=True)
    quantity = forms.IntegerField(min_value=1, required=True)

    class Meta:
        model = Part
        fields = ['item', 'color', 'list', 'quantity'] 

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Select an Excel file')

class QuantityForm(forms.Form):
    quantity = forms.IntegerField(required=True)
    item = forms.ModelChoiceField(queryset=Item.objects.all(), required=True)
    color = forms.ModelChoiceField(queryset=Color.objects.all(), required=True)
    selected_list = forms.ModelChoiceField(queryset=List.objects.all(), required=True)

class PartListForm(forms.ModelForm):
    list = forms.ModelChoiceField(queryset=List.objects.all(), empty_label=None, required=True)
    quantity = forms.IntegerField(min_value=1, required=True)

    class Meta:
        model = ListPart
        fields = ['list', 'quantity']

    def __init__(self, part_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter the queryset for the 'list' field to exclude lists that already have the part
        self.fields['list'].queryset = self.fields['list'].queryset.exclude(
            listpart__PartID_id=part_id
        )