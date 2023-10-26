from django.urls import path
from .views import Index, SignUpView, Dashboard, SetListView, SetListPartView, ListView, ItemView, ToggleView, ToggleAggregatedView, AddtoList, AddPart, AddListPart, EditPart, UpdateAvailableParts, EditPartQuantity, DeletePart, DeletePartFromList, GetValidSubtypesView, ImportItemsView, ImportPartsView, ImportSetPartsView, ItemDetailView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('setlistview/', SetListView.as_view(), name='setlistview'),
    path('setdetails/<int:setlist_id>/', SetListPartView.as_view(), name='setdetails'),
    path('listview/', ListView.as_view(), name='listview'),
    path('itemview/', ItemView.as_view(), name='itemview'),
    path('toggleview/', ToggleView.as_view(), name='toggleview'),
    path('toggleaggregatedview/', ToggleAggregatedView.as_view(), name='toggleaggregatedview'),
    path('item/<int:item_id>/', ItemDetailView.as_view(), name='itemdetail'),
    path('add_to_list/', AddtoList.as_view(), name='add_to_list'),
    path('add-part/', AddPart.as_view(), name='add-part'),
    path('add-list-part/<int:pk>/', AddListPart.as_view(), name='add-list-part'),
    path('edit-part/<int:pk>', EditPart.as_view(), name='edit-part'),
    path('edit_part_quantity/<int:pk>/', EditPartQuantity.as_view(), name='edit-part-quantity'),
    path('update_available_parts/<int:item_id>/', UpdateAvailableParts.as_view(), name='update_available_parts'),
    path('delete-part-list/<int:pk>/<int:list_id>/<str:list_name>/', DeletePartFromList.as_view(), name='delete-part-list'),
    path('delete-part/<int:pk>', DeletePart.as_view(), name='delete-part'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='bricks/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='bricks/logout.html'), name='logout'),
    path('get_valid_subtypes/', GetValidSubtypesView.as_view(), name='get_valid_subtypes'),
    path('import_items/', ImportItemsView.as_view(), name='import_items'),
    path('import_parts/', ImportPartsView.as_view(), name='import_parts'),
    path('import_set_parts/', ImportSetPartsView.as_view(), name='import_set_parts'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)