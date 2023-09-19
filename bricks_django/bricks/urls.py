from django.urls import path
from .views import Index, SignUpView, Dashboard, ListView, ItemView, ToggleView, AddPart, EditPart, EditPartQuantity, DeletePart, GetValidSubtypesView, ImportItemsView, ImportPartsView, ItemDetailView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('listview/', ListView.as_view(), name='listview'),
    path('itemview/', ItemView.as_view(), name='itemview'),
    path('toggleview/', ToggleView.as_view(), name='toggleview'),
    path('item/<int:item_id>/', ItemDetailView.as_view(), name='itemdetail'),
    path('add-part/', AddPart.as_view(), name='add-part'),
    path('edit-part/<int:pk>', EditPart.as_view(), name='edit-part'),
    path('edit_part_quantity/<int:pk>/', EditPartQuantity.as_view(), name='edit-part-quantity'),
    path('delete-part/<int:pk>', DeletePart.as_view(), name='delete-part'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='bricks/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='bricks/logout.html'), name='logout'),
    path('get_valid_subtypes/', GetValidSubtypesView.as_view(), name='get_valid_subtypes'),
    path('import_items/', ImportItemsView.as_view(), name='import_items'),
    path('import_parts/', ImportPartsView.as_view(), name='import_parts'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)