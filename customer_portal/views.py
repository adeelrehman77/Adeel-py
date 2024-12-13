
from django.shortcuts import render, redirect
from django.contrib import messages
from admin_dashboard.models import MenuList, TimeSlot, CustomerProfile, Subscription
from datetime import datetime, timedelta

def home(request):
    return render(request, 'customer_portal/home.html')

def menu_list(request):
    menus = MenuList.objects.filter(is_active=True)
    return render(request, 'customer_portal/menu_list.html', {'menus': menus})

def subscribe(request):
    if request.method == 'POST':
        try:
            customer = CustomerProfile.objects.create(
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                phone_number=request.POST['phone_number'],
                address=request.POST['address'],
                location=request.POST['location']
            )
            
            start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.POST['end_date'], '%Y-%m-%d').date()
            
            if (end_date - start_date).days > 30:
                messages.error(request, 'Subscription cannot exceed 30 days')
                return redirect('subscribe')
            
            subscription = Subscription.objects.create(
                customer=customer,
                menu_list_id=request.POST['menu_list'],
                time_slot_id=request.POST['time_slot'],
                start_date=start_date,
                end_date=end_date,
                selected_days=request.POST.getlist('weekdays'),
                payment_mode=request.POST['payment_mode'],
                delivery_notification=request.POST.get('delivery_notification', False)
            )
            messages.success(request, 'Subscription created successfully!')
            return redirect('home')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('subscribe')
    
    menus = MenuList.objects.filter(is_active=True)
    time_slots = TimeSlot.objects.filter(is_active=True)
    return render(request, 'customer_portal/subscribe.html', {
        'menus': menus,
        'time_slots': time_slots
    })
