
from django.contrib import admin
from .models import (
    Category, Item, MenuList, TimeSlot, CustomerProfile, 
    Subscription, DeliverySchedule, Notification, Payment, 
    Invoice, Report
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')

@admin.register(MenuList)
class MenuListAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'get_items_count')
    list_filter = ('is_active',)
    search_fields = ('name',)
    filter_horizontal = ('items',)

    def get_items_count(self, obj):
        return obj.items.count()
    get_items_count.short_description = 'Items Count'

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'is_active')
    list_filter = ('is_active',)
    ordering = ('start_time',)

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'phone_number', 'location')
    search_fields = ('user__first_name', 'user__last_name', 'phone_number')
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Customer Name'

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'menu', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('customer__user__first_name', 'customer__user__last_name')

@admin.register(DeliverySchedule)
class DeliveryScheduleAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'delivery_date', 'time_slot', 'status')
    list_filter = ('status', 'delivery_date')
    search_fields = ('subscription__customer__user__first_name',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'title', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('customer__user__first_name', 'title')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'payment_date', 'status')
    list_filter = ('status', 'payment_date')
    search_fields = ('subscription__customer__user__first_name',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'generated_at', 'is_paid')
    list_filter = ('is_paid', 'generated_at')
    search_fields = ('subscription__customer__user__first_name',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('type', 'date_from', 'date_to', 'total_revenue')
    list_filter = ('type', 'date_from', 'date_to')
