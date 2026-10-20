from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="bi-lightning-charge")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Shoe(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='shoes', db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='shoes', db_index=True)
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.9)
    review_count = models.PositiveIntegerField(default=48)
    image_url = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='shoes/', blank=True, null=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_trending = models.BooleanField(default=False, db_index=True)
    in_stock = models.BooleanField(default=True, db_index=True)
    material = models.CharField(max_length=200, default="AeroFiber Mesh & React Foam")
    cushioning = models.CharField(max_length=100, default="Air Max Pro 4D")
    weight = models.CharField(max_length=100, default="245g / 8.6 oz")
    release_year = models.PositiveIntegerField(default=2026)
    badge = models.CharField(max_length=50, blank=True, default="NEW RELEASE")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'price']),
            models.Index(fields=['is_featured', 'created_at']),
            models.Index(fields=['brand', 'price']),
        ]

    def __str__(self):
        return f"{self.title} - ${self.price}"

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            diff = self.original_price - self.price
            return int((diff / self.original_price) * 100)
        return 0

    @property
    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return "/static/images/shoe_neon_blaze.jpg"


class ShoeSize(models.Model):
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=10)
    stock_quantity = models.PositiveIntegerField(default=10)

    class Meta:
        unique_together = ('shoe', 'size')
        ordering = ['size']

    def __str__(self):
        return f"{self.shoe.title} - US {self.size} (Stock: {self.stock_quantity})"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_key = models.CharField(max_length=100, db_index=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.id} ({self.user.username if self.user else self.session_key})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE)
    size = models.CharField(max_length=10, default="9.5")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'shoe', 'size')

    def __str__(self):
        return f"{self.quantity}x {self.shoe.title} (US {self.size})"

    @property
    def subtotal(self):
        return self.shoe.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('PLACED', 'Order Placed'),
        ('INSPECTION', 'Quality Inspection Passed'),
        ('DISPATCHED', 'Dispatched from Warehouse'),
        ('IN_TRANSIT', 'In Transit to Destination'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered & Signed'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('CARD', 'Credit / Debit Card'),
        ('APPLE_PAY', 'Apple Pay / Google Pay'),
        ('COD', 'Cash on Delivery'),
    ]

    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    tracking_code = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField(db_index=True)
    customer_phone = models.CharField(max_length=50)
    shipping_address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=30)
    country = models.CharField(max_length=100, default="United States")
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PLACED', db_index=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='CARD')
    payment_status = models.CharField(max_length=20, default='PAID')
    courier_partner = models.CharField(max_length=100, default="FedEx Priority Express")
    current_location = models.CharField(max_length=150, default="Central Fulfillment Facility, JFK Airport")
    driver_name = models.CharField(max_length=100, default="Marcus Vance")
    driver_phone = models.CharField(max_length=50, default="+1 (800) 555-8392")
    estimated_delivery = models.CharField(max_length=100, default="Within 48 Hours")
    notes = models.TextField(blank=True, default="Signature required on delivery. Temperature-controlled protective packaging.")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} ({self.tracking_code}) - {self.status}"

    @property
    def progress_percentage(self):
        mapping = {
            'PLACED': 15,
            'INSPECTION': 35,
            'DISPATCHED': 55,
            'IN_TRANSIT': 75,
            'OUT_FOR_DELIVERY': 90,
            'DELIVERED': 100,
            'CANCELLED': 0,
        }
        return mapping.get(self.status, 20)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE)
    size = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.shoe.title} (Size {self.size})"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class TrackingUpdate(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='timeline')
    status_title = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.order.tracking_code} - {self.status_title}"


class SupportTicket(models.Model):
    ISSUE_CHOICES = [
        ('TRACKING', 'Delivery & Tracking Status'),
        ('SIZING', 'Shoe Sizing & Fit Help'),
        ('ORDER', 'Order Modification / Cancellation'),
        ('RETURN', 'Refund & Returns Policy'),
        ('QUALITY', 'Product Authenticity & Warranty'),
        ('OTHER', 'General Inquiry'),
    ]

    ticket_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    order_number = models.CharField(max_length=50, blank=True)
    issue_type = models.CharField(max_length=30, choices=ISSUE_CHOICES, default='TRACKING')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.subject}"


class ShoeReview(models.Model):
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(default=5)
    headline = models.CharField(max_length=150, default="Unbelievable comfort and style")
    comment = models.TextField()
    verified_purchase = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.shoe.title} - {self.rating} stars by {self.user_name}"
