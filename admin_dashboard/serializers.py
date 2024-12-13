
from rest_framework import serializers
from .models import Category, Item, MenuList, TimeSlot, CustomerProfile, Subscription

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'is_active']

class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'is_active', 'image', 
                 'preparation_time', 'customization_options', 'category', 'category_id']

class MenuListSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)
    item_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = MenuList
        fields = ['id', 'name', 'description', 'price', 'is_active', 'items', 'item_ids']

    def create(self, validated_data):
        item_ids = validated_data.pop('item_ids')
        menu_list = MenuList.objects.create(**validated_data)
        menu_list.items.set(item_ids)
        return menu_list

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'start_time', 'end_time', 'is_active']

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'address', 'location']

class SubscriptionSerializer(serializers.ModelSerializer):
    customer = CustomerProfileSerializer(read_only=True)
    menu_list = MenuListSerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'customer', 'menu_list', 'time_slot', 'start_date', 
                 'end_date', 'selected_days', 'payment_mode', 'delivery_notification']
        
    def validate(self, data):
        if (data['end_date'] - data['start_date']).days > 30:
            raise serializers.ValidationError("Subscription duration cannot exceed 30 days")
        return data

class DeliveryScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliverySchedule
        fields = ['id', 'subscription', 'delivery_date', 'status', 
                 'delivery_notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'customer', 'type', 'title', 'message', 'is_read', 'created_at']
        read_only_fields = ['created_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'subscription', 'amount', 'transaction_id', 'status', 
                 'payment_date', 'payment_method', 'notes']
        read_only_fields = ['payment_date']

class InvoiceSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'payment', 'invoice_number', 'generated_date', 
                 'due_date', 'is_paid']
        read_only_fields = ['invoice_number', 'generated_date']
