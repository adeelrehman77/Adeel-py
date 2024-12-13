
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
