
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Category, Item, MenuList, TimeSlot
from .serializers import CategorySerializer, ItemSerializer, MenuListSerializer, TimeSlotSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Category.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')
        return queryset

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Item.objects.all()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

class MenuListViewSet(viewsets.ModelViewSet):
    queryset = MenuList.objects.all()
    serializer_class = MenuListSerializer
    permission_classes = [IsAuthenticated]

class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAdminUser]

class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Subscription.objects.all()
        if not self.request.user.is_staff:
            customer_id = self.request.query_params.get('customer_id', None)
            if customer_id:
                queryset = queryset.filter(customer_id=customer_id)
        return queryset

class DeliveryScheduleViewSet(viewsets.ModelViewSet):
    queryset = DeliverySchedule.objects.all()
    serializer_class = DeliveryScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DeliverySchedule.objects.all()
        status = self.request.query_params.get('status', None)
        date = self.request.query_params.get('date', None)
        
        if status:
            queryset = queryset.filter(status=status)
        if date:
            queryset = queryset.filter(delivery_date=date)
        return queryset

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Notification.objects.all()
        customer_id = self.request.query_params.get('customer_id', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        return queryset

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Payment.objects.all()
        subscription_id = self.request.query_params.get('subscription_id', None)
        if subscription_id:
            queryset = queryset.filter(subscription_id=subscription_id)
        return queryset

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Invoice.objects.all()
        is_paid = self.request.query_params.get('is_paid', None)
        if is_paid is not None:
            queryset = queryset.filter(is_paid=is_paid == 'true')
        return queryset


from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import json

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def generate_report(self, start_date, end_date, report_type):
        subscriptions = Subscription.objects.filter(
            start_date__gte=start_date,
            end_date__lte=end_date
        )
        
        payments = Payment.objects.filter(
            payment_date__date__gte=start_date,
            payment_date__date__lte=end_date,
            status='SUCCESS'
        )
        
        report_data = {
            'subscription_count': subscriptions.count(),
            'revenue': float(payments.aggregate(Sum('amount'))['amount__sum'] or 0),
            'payment_methods': dict(payments.values_list('payment_method').annotate(count=Count('id'))),
            'active_customers': CustomerProfile.objects.filter(subscription__in=subscriptions).distinct().count()
        }
        
        return Report.objects.create(
            type=report_type,
            date_from=start_date,
            date_to=end_date,
            total_revenue=report_data['revenue'],
            total_subscriptions=report_data['subscription_count'],
            active_customers=report_data['active_customers'],
            data=report_data
        )

    @action(detail=False, methods=['post'])
    def generate(self, request):
        report_type = request.data.get('type', 'DAILY')
        today = timezone.now().date()
        
        if report_type == 'DAILY':
            start_date = today
            end_date = today
        elif report_type == 'WEEKLY':
            start_date = today - timedelta(days=7)
            end_date = today
        else:  # MONTHLY
            start_date = today - timedelta(days=30)
            end_date = today
            
        report = self.generate_report(start_date, end_date, report_type)
        return Response(self.get_serializer(report).data)
