
from django.shortcuts import render
from admin_dashboard.models import MenuList, TimeSlot, CustomerProfile, Subscription
from django.core.exceptions import ValidationError
from django.contrib import messages

def home(request):
    return render(request, 'customer_portal/home.html')

def menu_list(request):
    menus = MenuList.objects.filter(is_active=True)
    return render(request, 'customer_portal/menu_list.html', {'menus': menus})

def subscribe(request):
    if request.method == 'POST':
        try:
            # Form processing logic will go here
            pass
        except ValidationError as e:
            messages.error(request, str(e))
    
    time_slots = TimeSlot.objects.filter(is_active=True)
    menus = MenuList.objects.filter(is_active=True)
    return render(request, 'customer_portal/subscribe.html', {
        'time_slots': time_slots,
        'menus': menus
    })
