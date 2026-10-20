from rest_framework import serializers
from .models import Shoe, ShoeSize, Category, Brand, Order, OrderItem, TrackingUpdate, SupportTicket, ShoeReview

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description']

class ShoeSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoeSize
        fields = ['size', 'stock_quantity']

class ShoeReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoeReview
        fields = ['id', 'user_name', 'rating', 'headline', 'comment', 'verified_purchase', 'created_at']

class ShoeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    sizes = ShoeSizeSerializer(many=True, read_only=True)
    image_display = serializers.CharField(source='get_image_url', read_only=True)
    discount_percentage = serializers.IntegerField(source='discount_percent', read_only=True)

    class Meta:
        model = Shoe
        fields = [
            'id', 'title', 'slug', 'brand', 'brand_name', 'category', 'category_name',
            'tagline', 'description', 'price', 'original_price', 'rating', 'review_count',
            'image_display', 'is_featured', 'is_trending', 'in_stock', 'material',
            'cushioning', 'weight', 'release_year', 'badge', 'discount_percentage', 'sizes'
        ]

class TrackingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingUpdate
        fields = ['id', 'status_title', 'location', 'timestamp', 'is_completed', 'description']

class OrderItemSerializer(serializers.ModelSerializer):
    shoe_title = serializers.CharField(source='shoe.title', read_only=True)
    shoe_image = serializers.CharField(source='shoe.get_image_url', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'shoe_title', 'shoe_image', 'size', 'quantity', 'unit_price', 'subtotal']

class OrderTrackingSerializer(serializers.ModelSerializer):
    timeline = TrackingUpdateSerializer(many=True, read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_number', 'tracking_code', 'customer_name', 'shipping_address', 'city',
            'country', 'status', 'status_display', 'progress_percentage', 'total_amount',
            'courier_partner', 'current_location', 'driver_name', 'driver_phone',
            'estimated_delivery', 'notes', 'created_at', 'timeline', 'items'
        ]

class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['ticket_id', 'name', 'email', 'order_number', 'issue_type', 'subject', 'message', 'created_at']
        read_only_fields = ['ticket_id', 'created_at']
