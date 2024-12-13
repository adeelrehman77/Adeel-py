
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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('customer_portal.urls')),
]
