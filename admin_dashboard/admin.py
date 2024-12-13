
from django.contrib import admin
from .models import Category, Item, MenuList, TimeSlot, CustomerProfile, Subscription

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
    list_display = ('full_name', 'phone_number', 'location')
    search_fields = ('first_name', 'last_name', 'phone_number')
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Customer Name'

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'menu_list', 'start_date', 'end_date', 'payment_mode')
    list_filter = ('payment_mode', 'delivery_notification')
    search_fields = ('customer__first_name', 'customer__last_name')
    date_hierarchy = 'start_date'
