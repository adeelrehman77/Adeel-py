
from django.db import models
from django.core.validators import MaxValueValidator, RegexValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    image = models.URLField(blank=True)
    preparation_time = models.IntegerField(help_text="Preparation time in minutes", default=30)
    customization_options = models.JSONField(default=dict, blank=True, 
        help_text="Store customization options as JSON")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
        
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.is_active and self.menulist_set.filter(is_active=True).exists():
            raise ValidationError('Cannot deactivate item while it is part of an active menu')

class MenuList(models.Model):
    name = models.CharField(max_length=100)
    items = models.ManyToManyField(Item)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Optional package price")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.items.exists() and self.is_active:
            raise ValidationError('Cannot activate menu list without items')
        if self.items.filter(is_active=False).exists():
            raise ValidationError('Cannot include inactive items in menu list')

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"

class CustomerProfile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    address = models.TextField()
    location = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Subscription(models.Model):
    PAYMENT_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('CARD', 'Credit Card'),
    ]
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    menu_list = models.ForeignKey(MenuList, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    selected_days = models.JSONField()  # Store weekdays as JSON array
    payment_mode = models.CharField(max_length=4, choices=PAYMENT_CHOICES)
    delivery_notification = models.BooleanField(default=True)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import datetime
        delta = self.end_date - self.start_date
        if delta.days > 30:
            raise ValidationError('Subscription duration cannot exceed 30 days')

class DeliverySchedule(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('OUT', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    delivery_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    delivery_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['delivery_date', 'created_at']

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('DELIVERY', 'Delivery Update'),
        ('SUBSCRIPTION', 'Subscription Update'),
        ('MENU', 'Menu Update'),
        ('GENERAL', 'General Message')
    ]
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    type = models.CharField(max_length=12, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded')
    ]
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-payment_date']

class Invoice(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True)
    generated_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-invoice_number').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number[3:])
                self.invoice_number = f'INV{str(last_number + 1).zfill(6)}'
            else:
                self.invoice_number = 'INV000001'
        super().save(*args, **kwargs)


class Report(models.Model):
    REPORT_TYPES = [
        ('DAILY', 'Daily Report'),
        ('WEEKLY', 'Weekly Report'),
        ('MONTHLY', 'Monthly Report')
    ]
    
    type = models.CharField(max_length=10, choices=REPORT_TYPES)
    date_from = models.DateField()
    date_to = models.DateField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    total_subscriptions = models.IntegerField()
    active_customers = models.IntegerField()
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(help_text="Detailed report data in JSON format")

    class Meta:
        ordering = ['-generated_at']


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20)  # e.g., kg, liters, pieces
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=100, blank=True)
    last_restocked = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

    class Meta:
        ordering = ['name']


class IngredientUsage(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    date_used = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Update ingredient quantity when used
        self.ingredient.quantity -= self.quantity_used
        self.ingredient.save()
        super().save(*args, **kwargs)
