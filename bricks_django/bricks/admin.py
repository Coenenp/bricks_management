from django import forms
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.conf import settings
from .models import Part, List, ListPart, Color, Item, Type, Category, ItemAlias, SetList, SetPart, SetListPart

admin.site.register(Part)
admin.site.register(List)
admin.site.register(ListPart)
admin.site.register(Category)
admin.site.register(ItemAlias)
admin.site.register(SetList)
admin.site.register(SetListPart)
admin.site.register(SetPart)

class CustomItemAdminForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['SubtypeID'].queryset = Type.objects.none()
        self.fields['TypeID'].queryset = Type.objects.filter(ParentID=0)

        if self.instance.TypeID and hasattr(self.instance.TypeID, 'TypeID'):
            self.fields['SubtypeID'].queryset = Type.objects.filter(ParentID=self.instance.TypeID.TypeID)

        if selected_type_id := self['TypeID'].value():
            self.fields['SubtypeID'].queryset = Type.objects.filter(ParentID=selected_type_id)
            
    def clean_SubtypeID(self):
        subtype = self.cleaned_data.get('SubtypeID')
        selected_type = self.cleaned_data.get('TypeID')
        if subtype is not None and selected_type is not None:
            if subtype.ParentID != 0 and selected_type.TypeID != subtype.ParentID:
                raise forms.ValidationError('Invalid subtype for the selected type.')

        return subtype

class CustomColorAdminForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = '__all__'
        
class ParentTypeFilter(admin.SimpleListFilter):
    title = ('Parent Type')  # Displayed on the right side of the change list
    parameter_name = 'parent_type'

    def lookups(self, request, model_admin):
        parent_types = Type.objects.filter(ParentID=0)
        return [(str(parent_type.TypeID), parent_type.Name) for parent_type in parent_types]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(TypeID__TypeID=self.value())
        return queryset

class ItemAdmin(admin.ModelAdmin):
    list_display = ['Name', 'list_alias_names', 'Description', 'display_image', 'TypeID', 'SubtypeID', 'local_image']
    form = CustomItemAdminForm

    def list_alias_names(self, obj):
        # Retrieve all alias names for the item
        alias_names = ItemAlias.objects.filter(Item=obj).values_list('AliasName', flat=True)
        return format_html('<br>'.join(alias_names))
    
    list_alias_names.short_description = 'Alias Names'

    def display_image(self, obj):
        if obj.ImageReference:
            image_url = obj.ImageReference
            return format_html('<img src="{}" width="50" height="50" />', image_url)
        else:
            return ''
    display_image.short_description = 'Image'
    
    def local_image(self, obj):
        if obj.WebrickImageReference:
            image_url = obj.WebrickImageReference
            return format_html('<img src="{}" width="50" height="50" />', image_url)
        else:
            return ''
    local_image.short_description = 'Image'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload_excel/', self.admin_site.admin_view(self.upload_excel_view), name='upload_excel'),
        ]
        return custom_urls + urls

    def upload_excel_view(self, request):
        return HttpResponseRedirect(reverse('admin:import_items'))

    list_filter = [ParentTypeFilter]
    search_fields = ['Name', 'Description']
    ordering = ['ItemID']

class ColorAdmin(admin.ModelAdmin):
    list_display = ['Name', 'BricklinkColorID', 'WebrickColorID', 'ColorType', 'color_swatch']
    form = CustomColorAdminForm
    ordering = ['ColorID']

    def color_swatch(self, obj):
        color_style = f'background-color: {obj.RGB}; width: 30px; height: 30px; display: inline-block;'
        return format_html('<div style="{}"></div>', color_style)
    color_swatch.short_description = 'Color'
    
    list_filter = ['ColorType'] 
    search_fields = ['Name', 'BricklinkColorID', 'WebrickColorID', 'ColorType']
    
class TypeAdmin(admin.ModelAdmin):
    list_display = ['type_name', 'subtype_name']
    list_filter = []
    search_fields = ['Name']
    ordering = ['TypeID']

    def type_name(self, obj):
        # Display the name of the parent type
        return obj.Name
    
    def subtype_name(self, obj):
        # Display the names of subtypes for the parent type
        subtypes = Type.objects.filter(ParentID=obj.TypeID)
        return ', '.join(subtype.Name for subtype in subtypes)

    type_name.short_description = 'Parent Type'
    subtype_name.short_description = 'Subtypes'

admin.site.register(Type, TypeAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Color, ColorAdmin)