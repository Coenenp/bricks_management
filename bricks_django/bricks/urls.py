from django.urls import path
from .views import Index, SignUpView, Dashboard, SetListView, SetListPartView, ListView, ItemView, ToggleView, ToggleAggregatedView, AddtoList, AddPart, AddListPart, PartDetailView, UpdateAvailableParts, EditPartQuantity, DeletePart, DeleteItem, DeletePartFromList, ImportItemsView, ImportPartsView, ImportSetPartsView, ItemDetailView, GetSubtypesView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('setlistview/', SetListView.as_view(), name='setlistview'),
    path('set/<int:setlist_id>/', SetListPartView.as_view(), name='setdetail'),
    path('listview/', ListView.as_view(), name='listview'),
    path('itemview/', ItemView.as_view(), name='itemview'),
    path('toggleview/', ToggleView.as_view(), name='toggleview'),
    path('toggleaggregatedview/', ToggleAggregatedView.as_view(), name='toggleaggregatedview'),
    path('item/<int:item_id>/', ItemDetailView.as_view(), name='itemdetail'),
    path('add-to-list/', AddtoList.as_view(), name='add-to-list'),
    path('add-part/', AddPart.as_view(), name='add-part'),
    path('add-list-part/<int:pk>/', AddListPart.as_view(), name='add-list-part'),
    path('part/<int:pk>', PartDetailView.as_view(), name='partdetail'),
    path('edit_part_quantity/<int:pk>/', EditPartQuantity.as_view(), name='edit-part-quantity'),
    path('update_available_parts/<int:item_id>/', UpdateAvailableParts.as_view(), name='update_available_parts'),
    path('delete-part-list/<int:pk>/<int:list_id>/<str:list_name>/', DeletePartFromList.as_view(), name='delete-part-list'),
    path('delete-part/<int:pk>', DeletePart.as_view(), name='delete-part'),
    path('delete-item/<int:pk>', DeleteItem.as_view(), name='delete-item'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='bricks/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='bricks/logout.html'), name='logout'),
    path('import-items/', ImportItemsView.as_view(), name='import-items'),
    path('import-parts/', ImportPartsView.as_view(), name='import-parts'),
    path('import-set-parts/', ImportSetPartsView.as_view(), name='import-set-parts'),
    path('get-subtypes/', GetSubtypesView.as_view(), name='get-subtypes'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)