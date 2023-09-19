import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import F, Q
from .forms import UserRegisterForm, PartForm, ExcelUploadForm
from .models import Part, List, Item, Type, Color, ListPart, ItemAlias
from collections import defaultdict
from bricks_django.settings import MOC_PART

class ToggleView(View):
    http_method_names = ['post']  # Allow only POST requests

    def post(self, request):
        # Your view logic here
        if 'view_mode' in request.session:
            if request.session['view_mode'] == 'list':
                request.session['view_mode'] = 'array'
            else:
                request.session['view_mode'] = 'list'
        else:
            request.session['view_mode'] = 'array'  # Default to array view

        return JsonResponse({'new_mode': request.session['view_mode']})

class Index(TemplateView):
    template_name = 'bricks/index.html'
    
class Dashboard(LoginRequiredMixin, View, Paginator):
	def get(self, request):
		parts = Part.objects.order_by('ItemID')

		moc_parts = Part.objects.filter(listpart__ListID__CategoryID__pk=MOC_PART).order_by('ItemID')

		if moc_parts.count() > 0:
			messages.info(request, f'{moc_parts.count()} are MOC parts')

		moc_parts_ids = Part.objects.filter(listpart__ListID__CategoryID__pk=MOC_PART).order_by('ItemID').values_list('PartID', flat=True)

		items_per_page = 10
		paginator = Paginator(parts, items_per_page)
		page_number = request.GET.get('page')
		page_parts = paginator.get_page(page_number)

		return render(request, 'bricks/dashboard.html', {'page_parts': page_parts,'parts': parts, 'moc_parts_ids': moc_parts_ids})

class SignUpView(View):
	def get(self, request):
		form = UserRegisterForm()
		return render(request, 'bricks/signup.html', {'form': form})

	def post(self, request):
		form = UserRegisterForm(request.POST)

		if form.is_valid():
			form.save()
			user = authenticate(
				username=form.cleaned_data['username'],
				password=form.cleaned_data['password1']
			)

			login(request, user)
			return redirect('index')

		return render(request, 'bricks/signup.html', {'form': form})

class AddPart(LoginRequiredMixin, CreateView):
	model = Part
	form_class = PartForm
	template_name = 'bricks/add_part.html'
	success_url = reverse_lazy('dashboard')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['lists'] = List.objects.all()
		return context

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super().form_valid(form)

class EditPart(LoginRequiredMixin, UpdateView):
    model = Part
    form_class = PartForm
    template_name = 'bricks/edit_part.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        part = self.object

        # Add the part image to the context
        context['part_image'] = part.ImageReference

        # Get all lists for this part
        part_lists = part.listpart_set.all()

        # Create a list of dictionaries containing list and quantity
        part_lists_data = [{'list': list_part.ListID, 'quantity': list_part.Quantity} for list_part in part_lists]

        context['part_lists_data'] = part_lists_data

        # Get the previous and next parts
        previous_part = Part.objects.filter(date_created__lt=part.date_created).order_by('-date_created').first()
        next_part = Part.objects.filter(date_created__gt=part.date_created).order_by('date_created').first()

        if not next_part:
            # If there's no next part, wrap around to the first part
            next_part = Part.objects.order_by('date_created').first()

        if not previous_part:
            # If there's no previous part, wrap around to the last part
            previous_part = Part.objects.order_by('-date_created').first()

        context['previous_part'] = previous_part
        context['next_part'] = next_part

        return context
    
class EditPartQuantity(View):
    def post(self, request, *args, **kwargs):
        # Process the form data and update quantities
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                list_id = key.split('_')[1]
                quantity = int(value)
                # Update the ListPart record
                ListPart.objects.filter(ListID_id=list_id, PartID_id=kwargs['pk']).update(Quantity=quantity)
        
        # Return a JSON response indicating success
        return JsonResponse({'message': 'Quantities have been updated.'})
    
class DeletePart(LoginRequiredMixin, DeleteView):
	model = Part
	template_name = 'bricks/delete_part.html'
	success_url = reverse_lazy('dashboard')
	context_object_name = 'part'

class ListView(LoginRequiredMixin, View):
	def get(self, request):
		lists = List.objects.order_by('ListID')

		return render(request, 'bricks/listview.html', {'lists': lists})

class ItemView(LoginRequiredMixin, View):
    template_name = 'bricks/itemview.html'

    def get(self, request):
        view_mode = request.session.get('view_mode', 'list')
        
        # Fetch items and types
        items = Item.objects.order_by('Description')
        types = Type.objects.filter(ParentID=0)

        selected_type_id = request.GET.get('typeFilter')

        if selected_type_id:
            items = items.filter(TypeID=selected_type_id)

        context = {
            'items': items,
            'types': types,
            'view_mode': view_mode,
        }
        return render(request, self.template_name, context)
    
class ItemDetailView(View):
    def get(self, request, item_id):
        item = get_object_or_404(Item, pk=item_id)
        colors = Color.objects.filter(WebrickColorID__isnull=False)
        colors_by_type = defaultdict(list)
        lists = List.objects.all()

        previous_item_id = Item.objects.filter(pk__lt=item_id).order_by('-pk').first()
        next_item_id = Item.objects.filter(pk__gt=item_id).order_by('pk').first()
        # If there's no next item, wrap around to the first item
        if not next_item_id:
            next_item_id = Item.objects.order_by('pk').first()

        # If there's no previous item, wrap around to the last item
        if not previous_item_id:
            previous_item_id = Item.objects.order_by('-pk').first()
            
        # Iterate through your colors and group them by ColorType
        for color in colors:
            colors_by_type[color.ColorType].append(color)

        return render(
            request, 
            'bricks/itemdetail.html', 
            {
                'item': item, 
                'colors_by_type': dict(colors_by_type), 
                'lists': lists,
                'previous_item_id': previous_item_id.pk,
                'next_item_id': next_item_id.pk,
            },
        )
    
class GetValidSubtypesView(View):
    def get(self, request):
        type_id = request.GET.get('type_id')
        valid_subtypes = Type.objects.filter(ParentID=type_id).values('TypeID', 'Name')
        return JsonResponse(list(valid_subtypes), safe=False)

class ImportItemsView(View):
    template_name = 'bricks/import_items.html'
    
    def get(self, request):
        form = ExcelUploadForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['excel_file']
            try:
                df = pd.read_excel(excel_file)
                import_report = []

                for index, row in df.iterrows():
                    name = row['Name']
                    description = row['Description']
                    image_reference = row['ImageReference']
                    type_name = row['Type']
                    subtype_name = row['Subtype']
                    large_image_reference = row['LargeImageReference']

                    # Check if item with the same name already exists
                    try:
                        item = Item.objects.get(Name=name)
                        #import_report.append(f'Updated: {name}')
                    except Item.DoesNotExist:
                        item = Item(Name=name)
                        import_report.append(f'Created: {name}')

                    # Check if item name exists in ItemAlias table
                    #item_alias, created = ItemAlias.objects.get_or_create(AliasName=name, Item=item)
                    
                    # Check if item name exists in ItemAlias table                    
                    #if ItemAlias.objects.filter(AliasName=name).exists():
                    #    import_report.append(f'Skipped: {name} (Item alias already exists)')
                    #    continue

                    try:
                        item_type = Type.objects.get(Name=type_name, ParentID=0)
                        subtype = Type.objects.get(Name=subtype_name, ParentID=item_type.TypeID)
                    except Type.DoesNotExist:
                        import_report.append(f'Failed: {name} (Invalid Type or Subtype)')
                        continue

                    # Update the item fields only if they are NULL or empty
                    if description and (not item.Description):
                        item.Description = description
                    if image_reference and (not item.ImageReference):
                        item.ImageReference = image_reference
                    if large_image_reference and (not item.LargeImageReference):
                        item.LargeImageReference = large_image_reference

                    # Set Type and Subtype
                    item.TypeID = item_type
                    item.SubtypeID = subtype

                    item.save()  # Save the Item instance after related objects are saved

                return render(request, 'bricks/import_report.html', {'import_report': import_report})
            except Exception as e:
                return render(request, 'bricks/import_report.html', {'import_report': [f'Error: {str(e)}']})

        return render(request, self.template_name, {'form': form})

class ImportPartsView(View):
    template_name = 'bricks/import_parts.html'
    
    def get(self, request):
        form = ExcelUploadForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['excel_file']
            try:
                df = pd.read_excel(excel_file)
                import_report = []

                for index, row in df.iterrows():
                    item_name = row['ItemName']
                    color_id = row['WebrickColorID']
                    quantity = row['Quantity']
                    image_reference = row['ImageReferenceURL']
                    list_name = row['ListName']

                    # Check if the Item with the same name exists
                    try:
                        item = Item.objects.get(Name=item_name)
                    except Item.DoesNotExist:
                        import_report.append(f'Error: {item_name} (Item not found)')
                        continue

                    # Check if the Color with the given WebrickColorID exists
                    try:
                        color = Color.objects.get(WebrickColorID=color_id)
                    except Color.DoesNotExist:
                        import_report.append(f'Error: {item_name} (Color not found)')
                        continue

                    # Check if the List with the given ListName exists
                    try:
                        list = List.objects.get(Name=list_name)
                    except List.DoesNotExist:
                        import_report.append(f'Error: {item_name} (List not found)')
                        continue
                    
                    # Create or get the Part entry
                    part, created = Part.objects.get_or_create(
                        ItemID=item,
                        ColorID=color,
                        defaults={'ImageReference': image_reference}
                    )

                    # Try to get an existing ListPart entry
                    listpart = ListPart.objects.filter(ListID=list, PartID=part).first()
                    
                    if listpart:
                        # Update the quantity if the ListPart entry already exists
                        listpart.Quantity += quantity
                        listpart.save()
                        import_report.append(f'Success: {item_name} added to {list_name}, quantity updated to {listpart.Quantity}')
                    else:
                        # Create the ListPart entry if it doesn't already exist
                        ListPart.objects.create(
                            ListID=list,
                            PartID=part,
                            Quantity=quantity
                        )
                        import_report.append(f'Success: {item_name} added to {list_name}')

                return render(request, 'bricks/import_report.html', {'import_report': import_report})
            except Exception as e:
                return render(request, 'bricks/import_report.html', {'import_report': [f'Error: {str(e)}']})

        return render(request, self.template_name, {'form': form})
    
class ExcelUploadView(View):
    template_name = 'admin/upload_excel.html'

    def get(self, request):
        form = ExcelUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['excel_file']

            return HttpResponseRedirect('/admin/bricks/item/')
        return render(request, self.template_name, {'form': form})