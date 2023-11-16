import pandas as pd
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Sum, Q, F, ExpressionWrapper, IntegerField
from itertools import groupby
from operator import attrgetter, itemgetter
from .forms import UserRegisterForm, PartForm, PartListForm, ExcelUploadForm, QuantityForm
from .models import Part, List, Item, Type, Color, ListPart, ItemAlias, SetList, SetPart, SetListPart
from collections import defaultdict
from bricks_django.settings import MOC_PART

class ToggleView(View):
    http_method_names = ['post']  # Allow only POST requests

    def post(self, request):
        if (
            'view_mode' in request.session
            and request.session['view_mode'] == 'list'
            or 'view_mode' not in request.session
        ):
            request.session['view_mode'] = 'array'
        else:
            request.session['view_mode'] = 'list'
        return JsonResponse({'new_mode': request.session['view_mode']})

class ToggleAggregatedView(View):
    http_method_names = ['post']  # Allow only POST requests

    def post(self, request):
        if (
            'view_mode_dashboard' in request.session
            and request.session['view_mode_dashboard'] == 'part_view'
            or 'view_mode_dashboard' not in request.session
        ):
            request.session['view_mode_dashboard'] = 'aggregated_view'
        else:
            request.session['view_mode_dashboard'] = 'part_view'
        return JsonResponse({'new_mode': request.session['view_mode_dashboard']})

class Index(TemplateView):
    template_name = 'bricks/index.html'

class Dashboard(LoginRequiredMixin, View, Paginator):
    def get(self, request):
        view_mode = request.session.get('view_mode', 'aggregated_view')

        # Fetch distinct colors, types, and subtypes
        all_colors = Color.objects.filter(WebrickColorID__isnull=False).values('Name').distinct()
        all_types = Type.objects.filter(ParentID=0)
        all_subtypes = Type.objects.filter(~Q(ParentID=0))

        # Get the search query and filter values from request
        search_query = request.GET.get('q', '')
        color_filter = request.GET.get('colorFilter', '')
        type_filter = request.GET.get('typeFilter', '')
        subtype_filter = request.GET.get('subtypeFilter', '')

        #Get sort field and order
        sort_field = request.GET.get('sort', '')
        sort_order = request.GET.get('order', '')
        default_sort = ('PartID__ItemID', 'PartID__ColorID__Name')

        parts = ListPart.objects.select_related('PartID__ColorID').select_related('ListID__CategoryID').order_by(*default_sort)

        sort_field_mappings = {
            'item': ('PartID__ItemID__Name', 'PartID__ColorID__Name'),
            'color': ('PartID__ColorID__Name', 'PartID__ItemID__Name'),
        }

        if sort_field in sort_field_mappings:
            order_by = sort_field_mappings[sort_field]

            if sort_order == 'desc':
                order_by = tuple('-' + field for field in order_by)

            parts = parts.order_by(*order_by)

        # Filter parts based on the search query
        if search_query:
            parts = parts.filter(
                Q(PartID__ItemID__Name__icontains=search_query) |
                Q(PartID__ItemID__Description__icontains=search_query) |
                Q(PartID__ColorID__Name__icontains=search_query)
            )
        if color_filter and color_filter != "undefined":
            parts = parts.filter(PartID__ColorID__Name=color_filter)
        if type_filter and type_filter != "undefined":
            parts = parts.filter(PartID__ItemID__TypeID__TypeID=type_filter)
        if subtype_filter and subtype_filter != "undefined":
            parts = parts.filter(PartID__ItemID__SubtypeID__TypeID=subtype_filter)

        total_parts_quantity = parts.aggregate(total_quantity=Sum('Quantity'))['total_quantity']

        aggregated_data = []

        # Group parts by PartID for the aggregated view
        parts_grouped = groupby(parts, key=attrgetter('PartID'))

        for key, group in parts_grouped:
            # Create an empty dictionary to hold aggregated data for this part
            part_data = {
                'aggregated_part': None,
                'aggregated_quantity': 0,
                'part_lists': [],
            }

            for part in group:
                part_data['aggregated_part'] = part.PartID
                # Aggregate quantity for this part
                part_data['aggregated_quantity'] += part.Quantity
                # Get a list of lists where this part exists
                part_data['part_lists'] = List.objects.filter(listpart__PartID=part.PartID)

            # Add the part data to the aggregated data list
            aggregated_data.append(part_data)

        if sort_field == 'qty':
            order_by = ('Quantity', ) if sort_order == 'desc' else ('-Quantity', )
            parts = parts.order_by(*order_by)
            aggregated_data_order_by = lambda x: x['aggregated_quantity']
            aggregated_data = sorted(aggregated_data, key=aggregated_data_order_by, reverse=(sort_order == 'asc'))

        aggregated_data_count = len(aggregated_data)
        part_count = parts.count()

        # Create paginator for parts
        items_per_page = 50
        paginator_parts = Paginator(parts, items_per_page)
        page_number = request.GET.get('page', 1)
        page_parts = paginator_parts.get_page(page_number)

        # Create a separate paginator for aggregated parts
        aggregated_items_per_page = 50
        paginator_aggregated = Paginator(aggregated_data, aggregated_items_per_page)
        aggregated_page_number = request.GET.get('aggregated_page', 1)
        page_aggregated_data = paginator_aggregated.get_page(aggregated_page_number)

        # Filter MOC parts using ListPart model
        moc_parts = parts.filter(ListID__CategoryID__pk=MOC_PART).order_by('PartID__ItemID', 'PartID__ColorID')
        total_moc_quantity = moc_parts.aggregate(total_quantity=Sum('Quantity'))['total_quantity']
        moc_parts_ids = moc_parts.values_list('PartID', flat=True)

        if total_parts_quantity is None:
            messages.error(request, 'No bricks found matching your search criteria')
        elif moc_parts.count() > 0:
            messages.error(request, f'A total of {total_parts_quantity} bricks shown across {aggregated_data_count} parts. {total_moc_quantity} of those bricks are MOC parts.')
        else:
            messages.info(request, f'A total of {total_parts_quantity} bricks shown across {aggregated_data_count} parts.')

        context = {
            'page_parts': page_parts,
            'parts': parts,
            'aggregated_data': aggregated_data,
            'page_aggregated_data': page_aggregated_data,
            'moc_parts_ids': moc_parts_ids,
            'search_query': search_query,
            'total_parts_quantity': total_parts_quantity,
            'total_moc_quantity': total_moc_quantity,
            'all_colors': all_colors,
            'all_types': all_types,
            'all_subtypes': all_subtypes,
            'view_mode': view_mode,
            'sort': sort_field,
            'order': sort_order,
            'q': search_query,
            'colorFilter': color_filter,
            'typeFilter': type_filter,
            'subtypeFilter': subtype_filter,
        }

        return render(request, 'bricks/dashboard.html', context)


class ListView(LoginRequiredMixin, View):
    def get(self, request):
        lists = List.objects.order_by('ListID')
        
        list_data = []
        
        for list_item in lists:
            # Calculate the number of unique PartIDs for the current ListID
            unique_part_count = ListPart.objects.filter(ListID=list_item).values('PartID').distinct().count()

            # Calculate the sum of quantities for the current ListID
            total_quantity = ListPart.objects.filter(ListID=list_item).aggregate(total_quantity=Sum('Quantity'))['total_quantity']

            list_data.append({
                'list': list_item,
                'unique_part_count': unique_part_count,
                'total_quantity': total_quantity,
            })

        return render(request, 'bricks/listview.html', {
            'list_data': list_data,
        })

class SetListPartView(LoginRequiredMixin, View):
    def get(self, request, setlist_id):
        setlist = get_object_or_404(SetList, pk=setlist_id)

        # Get the SetListPart instances for the given SetList
        setlist_parts = SetListPart.objects.filter(SetListID=setlist)

        # Create a list to store the SetPart and total quantity data
        setpart_data = []

        previous_setlist = SetList.objects.filter(pk__lt=setlist_id).order_by('-pk').first()
        next_setlist = SetList.objects.filter(pk__gt=setlist_id).order_by('pk').first()

        set_items = SetPart.objects.filter(setlistpart__SetListID=setlist).distinct().count()

        # Calculate the total set quantity using aggregation
        set_pieces = setlist_parts.aggregate(total_quantity=Sum('Quantity'))['total_quantity'] or 0

        # If there's no next item, wrap around to the first item
        if not next_setlist:
            next_setlist = SetList.objects.order_by('pk').first()

        # If there's no previous item, wrap around to the last item
        if not previous_setlist:
            previous_setlist = SetList.objects.order_by('-pk').first()

        other_colors_dict = {}

        for setlist_part in setlist_parts:
            set_part_id = setlist_part.SetPartID_id  # Access the ID of the SetPart directly
            item_id = setlist_part.SetPartID.ItemID
            color_id = setlist_part.SetPartID.ColorID

            # Attempt to get the part, handling Part.DoesNotExist exception
            try:
                part = Part.objects.get(ItemID=item_id, ColorID=color_id)
            except Part.DoesNotExist:
                part = None

            # Calculate 'quantity' as the total quantity of the SetPart
            quantity = setlist_parts.filter(SetPartID=set_part_id).aggregate(
                quantity=Sum('Quantity')
            )['quantity'] or 0

            # Calculate 'total_quantity' using aggregation
            total_quantity = ListPart.objects.filter(PartID=part).aggregate(
                total_quantity=Sum('Quantity')
            )['total_quantity'] or 0

            # Calculate 'other_colors' as the sum of quantities for all Parts with the same ItemID but different ColorID
            other_colors = 0  # Reset other_colors for each SetPart
            other_colors += ListPart.objects.filter(
                PartID__ItemID=item_id
            ).exclude(PartID__ColorID=color_id).aggregate(
                other_colors_quantity=Sum('Quantity')
            )['other_colors_quantity'] or 0
            other_colors_dict[item_id] = other_colors

            # Create a dictionary to store the data
            setpart_info = {
                'setpart': setlist_part.SetPartID,
                'quantity': quantity,
                'part': part,
                'other_colors': other_colors,
                'total_quantity': total_quantity,
            }

            # Add the dictionary to the setpart_data list
            setpart_data.append(setpart_info)

        context = {
            'setlist': setlist,
            'set_items': set_items,
            'set_pieces': set_pieces,
            'setpart_data': setpart_data,
            'previous_setlist_id': previous_setlist.pk if previous_setlist else None,
            'next_setlist_id': next_setlist.pk if next_setlist else None,
        }
        return render(request, 'bricks/setdetail.html', context)

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
    template_name = 'bricks/add-part.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lists'] = List.objects.all()
        return context

    def form_valid(self, form):
        item = form.cleaned_data['item']
        color = form.cleaned_data['color']
        selected_list = form.cleaned_data['list']
        quantity = form.cleaned_data['quantity']

        # Get the currently logged-in user
        user = self.request.user

        # Check if the part already exists
        try:
            part = Part.objects.get(ItemID=item, ColorID=color)
        except Part.DoesNotExist:
            # If it doesn't exist, create it
            part = Part.objects.create(ItemID=item, ColorID=color, user=user)

        # Check if the part already exists in the list
        try:
            list_part = ListPart.objects.get(ListID=selected_list, PartID=part)
            # If it exists, update the quantity
            list_part.Quantity += quantity
            list_part.save()
        except ListPart.DoesNotExist:
            # If it doesn't exist, create it
            list_part = ListPart.objects.create(ListID=selected_list, PartID=part, Quantity=quantity)

        return redirect(self.success_url)
    
class AddListPart(LoginRequiredMixin, CreateView):
    model = ListPart
    form_class = PartListForm
    template_name = 'bricks/add-list-part.html'

    def form_valid(self, form):
        part_id = self.kwargs['pk']
        part = get_object_or_404(Part, pk=part_id)

        # Get the selected list from the form
        selected_list = form.cleaned_data['list']

        # Create a new ListPart instance with Part, List, and Quantity
        list_part = ListPart(
            ListID=selected_list,
            PartID=part,
            Quantity=form.cleaned_data['quantity']
        )

        # Save the ListPart instance
        list_part.save()

        if referring_url := self.request.session.get('referring_url'):
            return redirect(referring_url)
        else:
            return redirect('itemview')

    def get_form_kwargs(self):
        # Pass the part_id to the form during initialization
        kwargs = super().get_form_kwargs()
        kwargs['part_id'] = self.kwargs['pk']
        return kwargs

class PartDetailView(LoginRequiredMixin, UpdateView):
    model = Part
    form_class = PartForm
    template_name = 'bricks/partdetail.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        part = self.object

        # Add the part image to the context
        context['part_image'] = part.ImageReference
        context['part_name'] = part.ItemID.Name

        # Get all lists for this part
        part_lists = part.listpart_set.all()

        # Create a list of dictionaries containing list and quantity
        part_lists_data = [{'list': list_part.ListID, 'quantity': list_part.Quantity} for list_part in part_lists]

        context['part_lists_data'] = part_lists_data

        # Get the previous and next parts
        previous_part = Part.objects.filter(date_created__lt=part.date_created).order_by('-date_created').first() or Part.objects.order_by('-date_created').first()
        next_part = Part.objects.filter(date_created__gt=part.date_created).order_by('date_created').first() or Part.objects.order_by('date_created').first()

        context['previous_part'] = previous_part
        context['next_part'] = next_part

        # Set the referring URL in the session
        referring_url = reverse('partdetail', args=[part.pk])
        self.request.session['referring_url'] = referring_url

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

class UpdateAvailableParts(View):
    def post(self, request, item_id):
        parts_data = []
        item = get_object_or_404(Item, pk=item_id)
        parts = Part.objects.filter(ItemID=item)

        for part in parts:
            # Query ListPart instances related to the current part
            list_parts = ListPart.objects.filter(PartID=part).select_related('ListID__CategoryID')

            # Calculate the total quantity by summing the quantities from all ListPart instances
            total_quantity = list_parts.aggregate(total_quantity=models.Sum('Quantity'))['total_quantity'] or 0

            # Create a list of lists where the part appears
            appearing_lists = [list_part.ListID for list_part in list_parts]

            # Create a dictionary for the part's data
            part_info = {
                'part': {
                    'id': part.PartID,
                    'image': part.InternalURL.url if part.InternalURL else '',
                    'colorid': part.ColorID.ColorID,
                    'colorname': part.ColorID.Name,
                    'RGB': part.ColorID.RGB,
                    'HEX': part.ColorID.HEX,
                },
                'total_quantity': total_quantity,
                'appearing_lists': [
                    {
                        'list_id': list.ListID,
                        'category': list.CategoryID.Name,
                        'name': list.Name,
                    } for list in appearing_lists
                ],
            }

            # Append the part's data to the list
            parts_data.append(part_info)

        parts_data.sort(key=lambda x: x['total_quantity'], reverse=True)

        return JsonResponse({'success': True, 'parts_data': parts_data})

class DeletePart(LoginRequiredMixin, DeleteView):
    model = Part
    template_name = 'bricks/delete-part.html'
    context_object_name = 'part'
    success_url = reverse_lazy('dashboard')  # Default success URL

    def get_success_url(self):
        referring_url = self.request.session.get('referring_url', '')
        return referring_url or self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['go_back_url'] = self.request.session.get('referring_url', self.success_url)
        return context

    def get(self, request, *args, **kwargs):
        referring_url = request.META.get('HTTP_REFERER', '')
        if referring_url:
            request.session['referring_url'] = referring_url
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if 'referring_url' in self.request.session:
            del self.request.session['referring_url']  # Clear the session variable after use
        return HttpResponseRedirect(success_url)

class DeleteItem(LoginRequiredMixin, DeleteView):
	model = Item
	template_name = 'bricks/delete-item.html'
	success_url = reverse_lazy('itemview')
	context_object_name = 'item'

class DeletePartFromList(LoginRequiredMixin, View):
    template_name = 'bricks/delete-part-list.html'  # Use the confirmation template

    def get(self, request, *args, **kwargs):
        # Retrieve the part and list information for confirmation
        part_id = kwargs['pk']
        list_id = kwargs['list_id']
        list_name = kwargs['list_name']
        part = get_object_or_404(Part, PartID=part_id)
        
        context = {
            'part': part,
            'list_id': list_id,
            'list_name': list_name,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Handle the post request to delete the part from the list
        part_id = request.POST['part_id']
        list_id = request.POST['list_id']
        list_name = request.POST['list_name']

        part = get_object_or_404(Part, PartID=part_id)
        list_part = get_object_or_404(ListPart, PartID=part, ListID=list_id)

        # Delete the ListPart entry
        list_part.delete()
        messages.success(request, f'Part {part.ItemID} removed from list {list_name}')
        
        # If this was the last ListPart entry for this Part, you might want to delete the Part as well
        other_list_parts = ListPart.objects.filter(PartID=part)
        if not other_list_parts.exists():
            # Delete the Part if it's not associated with any other lists
            part.delete()
            messages.success(request, f'Successfully removed part {part.ItemID}')

        return redirect('dashboard')

class SetListView(LoginRequiredMixin, View):
    def get(self, request):
        setlists = SetList.objects.order_by('SetListID')
        
        setlist_data = []
        
        for setlist_item in setlists:
            # Calculate the number of unique PartIDs for the current ListID
            unique_part_count = SetListPart.objects.filter(SetListID=setlist_item).values('SetPartID').distinct().count()

            # Calculate the sum of quantities for the current ListID
            total_quantity = SetListPart.objects.filter(SetListID=setlist_item).aggregate(total_quantity=Sum('Quantity'))['total_quantity']

            setlist_data.append({
                'setlist': setlist_item,
                'unique_part_count': unique_part_count,
                'total_quantity': total_quantity,
            })

        return render(request, 'bricks/setlistview.html', {
            'setlist_data': setlist_data,
        })


class ItemView(LoginRequiredMixin, View):
    template_name = 'bricks/itemview.html'

    def get(self, request):
        view_mode = request.session.get('view_mode', 'list')
        
        # Get the search query and filter values from request
        search_query = request.GET.get('q', '')
        selected_type = request.GET.get('typeFilter', '')
        selected_subtype = request.GET.get('subtypeFilter', '')

        # Fetch items and types
        items = Item.objects.all()
        types = Type.objects.filter(ParentID=0)
        subtypes = Type.objects.filter(~Q(ParentID=0))
        
        #Get sort field and order
        sort_field = request.GET.get('sort', '')
        sort_order = request.GET.get('order', '') 
        default_sort = ('Description',)
        
        items = items.order_by(*default_sort)

        sort_field_mappings = {
            'id': ('ItemID',),
            'name': ('Name',),
            'description': ('Description',),
        }
        if sort_field in sort_field_mappings:
            order_by = sort_field_mappings[sort_field]

            if sort_order == 'desc':
                order_by = tuple(['-' + field for field in order_by])

            items = items.order_by(*order_by)

        # Filter parts based on the search query
        if search_query:
            items = items.filter(
                Q(Name__icontains=search_query) |
                Q(Description__icontains=search_query)
            )

        if selected_type and selected_type != "undefined":
            items = items.filter(TypeID=selected_type)
        if selected_subtype and selected_subtype != "undefined":
            items = items.filter(SubtypeID=selected_subtype)
            
        if items.count() > 0:
            messages.info(request, f'A total of {items.count()} items out of {Item.objects.count()} shown.')
        else:
            messages.error(request, f'No items found matching your search criteria. {Item.objects.count()} available.')

        items_per_page = 50
        paginator_parts = Paginator(items, items_per_page)
        page_number = request.GET.get('page', 1)
        page_items = paginator_parts.get_page(page_number)

        context = {
            'items': items,
            'types': types,
            'subtypes': subtypes,
            'q': search_query,
            'view_mode': view_mode,
            'page_items': page_items,
            'sort': sort_field,
            'order': sort_order,
            'search_query': search_query,
            'selected_type': selected_type,
            'selected_subtype': selected_subtype,
        }
        return render(request, self.template_name, context)
    
class ItemDetailView(LoginRequiredMixin, View):
    def get(self, request, item_id):
        initial_color_id = 1
        item = get_object_or_404(Item, pk=item_id)
        colors = Color.objects.filter(WebrickColorID__isnull=False)
        colors_by_type = defaultdict(list)
        lists = List.objects.all()
        parts = Part.objects.filter(ItemID=item)
        
        parts_data = []

        for part in parts:
            # Query ListPart instances related to the current part
            list_parts = ListPart.objects.filter(PartID=part)
            
            # Calculate the total quantity by summing the quantities from all ListPart instances
            total_quantity = list_parts.aggregate(total_quantity=models.Sum('Quantity'))['total_quantity'] or 0

            # Create a list of lists where the part appears
            appearing_lists = [list_part.ListID for list_part in list_parts]

            # Create a dictionary for the part's data
            part_info = {
                'part': part,
                'total_quantity': total_quantity,
                'appearing_lists': appearing_lists,
            }

            # Append the part's data to the list
            parts_data.append(part_info)

        parts_data.sort(key=lambda x: x['total_quantity'], reverse=True)

        previous_item = Item.objects.filter(pk__lt=item_id).order_by('-pk').first() or Item.objects.order_by('-pk').first()
        next_item = Item.objects.filter(pk__gt=item_id).order_by('pk').first() or Item.objects.order_by('pk').first()

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
                'parts': parts,
                'parts_data': parts_data,
                'previous_item_id': previous_item.pk if previous_item else None,
                'next_item_id': next_item.pk if next_item else None,
                'initial_color_id': initial_color_id,
            },
        )

class AddtoList(LoginRequiredMixin, View):
    def get(self, request):
        form = QuantityForm()
        return render(request, 'itemdetail.html', {'form': form})
    
    def post(self, request):
        form = QuantityForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            item = form.cleaned_data['item']
            color = form.cleaned_data['color']
            selected_list = form.cleaned_data['selected_list']
            
            # Get the currently logged-in user
            user = self.request.user

            try:
                part = Part.objects.get(ItemID=item, ColorID=color)
            except Part.DoesNotExist:
                part = Part.objects.create(ItemID=item, ColorID=color, user=user)

            try:
                list_part = ListPart.objects.get(ListID=selected_list, PartID=part)
                list_part.Quantity += quantity
                list_part.save()
            except ListPart.DoesNotExist:
                list_part = ListPart.objects.create(ListID=selected_list, PartID=part, Quantity=quantity)

            response_data = {
                'success': True,
                'message': 'Item added to the list successfully.'
            }
            return JsonResponse(response_data)
        
        else:   
            errors = form.errors.as_json() 
            response_data = {
                'success': False,
                'message': 'Invalid form data.',
                'errors': errors
            }
            return JsonResponse(response_data, status=400)

class ImportItemsView(LoginRequiredMixin, View):
    template_name = 'bricks/import-items.html'
    
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
                    webrick_image_reference = row['WebrickImageReference']

                    # Check if item with the same name already exists
                    try:
                        item = Item.objects.get(Name=name)
                        #import_report.append(f'Updated: {name}')
                    except Item.DoesNotExist:
                        item = Item(Name=name)
                        import_report.append(f'Created: {name}')

                    # Check if item name exists in ItemAlias table                    
                    if ItemAlias.objects.filter(AliasName=name).exists():
                        import_report.append(f'Skipped: {name} (Item alias already exists)')
                        continue

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
                    #if webrick_image_reference and (not item.WebrickImageReference):
                    item.WebrickImageReference = webrick_image_reference

                    # Set Type and Subtype
                    item.TypeID = item_type
                    item.SubtypeID = subtype

                    item.save()  # Save the Item instance after related objects are saved

                return render(request, 'bricks/import-report.html', {'import_report': import_report})
            except Exception as e:
                return render(request, 'bricks/import-report.html', {'import_report': [f'Error: {str(e)}']})

        return render(request, self.template_name, {'form': form})

class ImportPartsView(LoginRequiredMixin, View):
    template_name = 'bricks/import-parts.html'
    
    def get(self, request):
        form = ExcelUploadForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        user = self.request.user
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
                        try:
                            alias = ItemAlias.objects.get(AliasName=item_name)
                            item = alias.Item
                        except ItemAlias.DoesNotExist:
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
                        defaults={'ImageReference': image_reference},
                        user=user
                    )
                    # Check if a new Part was created
                    if created:
                        import_report.append(f'New Part created: {item_name}')

                    if listpart := ListPart.objects.filter(
                        ListID=list, PartID=part
                    ).first():
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

                return render(request, 'bricks/import-report.html', {'import_report': import_report})
            except Exception as e:
                return render(request, 'bricks/import-report.html', {'import_report': [f'Error: {str(e)}']})

        return render(request, self.template_name, {'form': form})

class ImportSetPartsView(LoginRequiredMixin, View):
    template_name = 'bricks/import-set-parts.html'
    
    def get(self, request):
        form = ExcelUploadForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        user = self.request.user
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
                    setlist_name = row['SetListName']

                    # Check if the Item with the same name exists
                    try:
                        item = Item.objects.get(Name=item_name)
                    except Item.DoesNotExist:
                        try:
                            alias = ItemAlias.objects.get(AliasName=item_name)
                            item = alias.Item
                        except ItemAlias.DoesNotExist:
                            import_report.append(f'Error: {item_name} (Item not found)')
                            continue

                    # Check if the Color with the given WebrickColorID exists
                    try:
                        color = Color.objects.get(WebrickColorID=color_id)
                    except Color.DoesNotExist:
                        import_report.append(f'Error: {item_name} (Color not found)')
                        continue

                    # Check if the SetList with the given SetListName exists
                    try:
                        setlist = SetList.objects.get(Name=setlist_name)
                    except SetList.DoesNotExist:
                        import_report.append(f'Error: {item_name} (Set not found)')
                        continue

                    # Create or get the SetPart entry
                    setpart, created = SetPart.objects.get_or_create(
                        ItemID=item,
                        ColorID=color,
                        defaults={'ImageReference': image_reference},
                        user=user
                    )

                    # Check if a new SetPart was created
                    if created:
                        import_report.append(f'New Set Part created: {item_name}')

                    if setlistpart := SetListPart.objects.filter(
                        SetListID=setlist, SetPartID=setpart
                    ).first():
                        # Update the quantity if the Set Part entry already exists
                        setlistpart.Quantity += quantity
                        setlistpart.save()
                        import_report.append(f'Success: {item_name} added to {setlist_name}, quantity updated to {setlistpart.Quantity}')
                    else:
                        # Create the SetPart entry if it doesn't already exist
                        SetListPart.objects.create(
                            SetListID=setlist,
                            SetPartID=setpart,
                            Quantity=quantity
                        )
                        import_report.append(f'Success: {item_name} added to {setlist_name}')

                return render(request, 'bricks/import-report.html', {'import_report': import_report})
            except Exception as e:
                return render(request, 'bricks/import-report.html', {'import_report': [f'Error: {str(e)}']})

        return render(request, self.template_name, {'form': form})

class GetSubtypesView(View):
    def get(self, request):
        # Get the selected type from the request's query parameters
        selected_type = request.GET.get("type", "")

        # Initialize an empty list to store subtypes
        subtypes = []

        # If a type is selected, filter subtypes based on the selected type
        if selected_type:
            subtypes = Type.objects.filter(ParentID=selected_type).values("TypeID", "Name")

        # Return the subtypes as JSON response
        return JsonResponse(list(subtypes), safe=False)