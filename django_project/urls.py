
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from admin_dashboard.views import CategoryViewSet, ItemViewSet, MenuListViewSet, TimeSlotViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'items', ItemViewSet)
router.register(r'menus', MenuListViewSet)
router.register(r'timeslots', TimeSlotViewSet)
router.register(r'customers', CustomerProfileViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'deliveries', DeliveryScheduleViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'reports', ReportViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'ingredient-usage', IngredientUsageViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('customer_portal.urls')),
]
