
from django.contrib import admin
from .models import Category, Item, MenuList, TimeSlot, CustomerProfile, Subscription

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(MenuList)
admin.site.register(TimeSlot)
admin.site.register(CustomerProfile)
admin.site.register(Subscription)
