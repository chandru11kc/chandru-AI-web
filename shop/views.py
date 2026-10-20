from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    Shoe, ShoeSize, Category, Brand, Cart, CartItem,
    Order, OrderItem, TrackingUpdate, SupportTicket, ShoeReview
)
from .utils import get_or_create_cart, generate_tracking_code, generate_order_number
from .serializers import ShoeSerializer, OrderTrackingSerializer, SupportTicketSerializer

# --- PAGE VIEWS ---

def home_view(request):
    """
    Landing Page: Hero presentation, featured & trending showcases, brand specs.
    """
    featured_shoes = Shoe.objects.filter(is_featured=True, in_stock=True).select_related('brand', 'category')[:6]
    trending_shoes = Shoe.objects.filter(is_trending=True, in_stock=True).select_related('brand', 'category')[:4]
    categories = Category.objects.annotate(shoe_count=Count('shoes'))
    latest_reviews = ShoeReview.objects.select_related('shoe').order_by('-created_at')[:4]
    hero_shoe = featured_shoes.first() if featured_shoes else None

    context = {
        'hero_shoe': hero_shoe,
        'featured_shoes': featured_shoes,
        'trending_shoes': trending_shoes,
        'categories': categories,
        'latest_reviews': latest_reviews,
    }
    return render(request, 'shop/home.html', context)


def store_view(request):
    """
    Shop / Store catalog with multi-filter: category, brand, price range, sizing, search, sorting.
    """
    shoes = Shoe.objects.select_related('brand', 'category').prefetch_related('sizes').filter(in_stock=True)

    # Search Query
    q = request.GET.get('q', '').strip()
    if q:
        shoes = shoes.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(brand__name__icontains=q) |
            Q(category__name__icontains=q) |
            Q(material__icontains=q)
        )

    # Filter Category
    category_slug = request.GET.get('category', '').strip()
    if category_slug:
        shoes = shoes.filter(category__slug=category_slug)

    # Filter Brand
    brand_slug = request.GET.get('brand', '').strip()
    if brand_slug:
        shoes = shoes.filter(brand__slug=brand_slug)

    # Filter Max Price
    max_price = request.GET.get('max_price', '').strip()
    if max_price:
        try:
            shoes = shoes.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Filter Size
    size_filter = request.GET.get('size', '').strip()
    if size_filter:
        shoes = shoes.filter(sizes__size=size_filter, sizes__stock_quantity__gt=0).distinct()

    # Sorting
    sort = request.GET.get('sort', 'featured')
    if sort == 'price_low':
        shoes = shoes.order_by('price')
    elif sort == 'price_high':
        shoes = shoes.order_by('-price')
    elif sort == 'rating':
        shoes = shoes.order_by('-rating')
    elif sort == 'newest':
        shoes = shoes.order_by('-created_at')
    else:
        shoes = shoes.order_by('-is_featured', '-is_trending', '-created_at')

    # Pagination for performance under high traffic
    paginator = Paginator(shoes, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.annotate(count=Count('shoes'))
    brands = Brand.objects.annotate(count=Count('shoes'))
    available_sizes = ["7.5", "8.0", "8.5", "9.0", "9.5", "10.0", "10.5", "11.0", "11.5", "12.0"]

    context = {
        'page_obj': page_obj,
        'shoes': page_obj.object_list,
        'categories': categories,
        'brands': brands,
        'available_sizes': available_sizes,
        'current_category': category_slug,
        'current_brand': brand_slug,
        'current_max_price': max_price,
        'current_size': size_filter,
        'current_sort': sort,
        'query': q,
        'total_count': paginator.count,
    }
    return render(request, 'shop/store.html', context)


def shoe_detail_view(request, slug):
    """
    Shoe detail showcase: high-res visuals, specs, sizing, customer reviews.
    """
    shoe = get_object_or_404(
        Shoe.objects.select_related('brand', 'category').prefetch_related('sizes', 'reviews'),
        slug=slug
    )
    related_shoes = Shoe.objects.filter(category=shoe.category).exclude(id=shoe.id)[:4]
    sizes = shoe.sizes.filter(stock_quantity__gt=0)
    reviews = shoe.reviews.all().order_by('-created_at')

    context = {
        'shoe': shoe,
        'related_shoes': related_shoes,
        'sizes': sizes,
        'reviews': reviews,
    }
    return render(request, 'shop/shoe_detail.html', context)


def cart_view(request):
    """
    Shopping Cart view with promo code calculation and order summary.
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('shoe', 'shoe__brand').all()
    subtotal = cart.subtotal
    
    # Check coupon discount in session
    coupon_code = request.session.get('coupon_code', '')
    discount = Decimal('0.00')
    if coupon_code.upper() == 'KICKS20':
        discount = subtotal * Decimal('0.20')
    elif coupon_code.upper() == 'FREESHIP':
        discount = Decimal('15.00')

    shipping = Decimal('0.00') if subtotal >= Decimal('150.00') or coupon_code.upper() == 'FREESHIP' else Decimal('15.00')
    if subtotal == 0:
        shipping = Decimal('0.00')
    total = max(Decimal('0.00'), subtotal - discount + shipping)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'total': total,
        'coupon_code': coupon_code,
    }
    return render(request, 'shop/cart.html', context)


def apply_coupon_view(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip().upper()
        if code in ['KICKS20', 'FREESHIP', 'SOLE10']:
            request.session['coupon_code'] = code
            messages.success(request, f"Promo code '{code}' applied successfully!")
        else:
            messages.error(request, "Invalid promo code. Try 'KICKS20' or 'FREESHIP'.")
    return redirect('cart')


def checkout_view(request):
    """
    Checkout Page: Shipping details, payment choice, generates order and real-time tracking code.
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('shoe').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty. Add shoes before proceeding to checkout.")
        return redirect('store')

    subtotal = cart.subtotal
    coupon_code = request.session.get('coupon_code', '')
    discount = Decimal('0.00')
    if coupon_code == 'KICKS20':
        discount = subtotal * Decimal('0.20')
    elif coupon_code == 'FREESHIP':
        discount = Decimal('15.00')
    shipping = Decimal('0.00') if subtotal >= Decimal('150.00') or coupon_code == 'FREESHIP' else Decimal('15.00')
    total = max(Decimal('0.00'), subtotal - discount + shipping)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        country = request.POST.get('country', 'United States').strip()
        payment_method = request.POST.get('payment_method', 'CARD')

        if not (name and email and phone and address and city and postal_code):
            messages.error(request, "Please fill in all required shipping fields.")
            return redirect('checkout')

        order_num = generate_order_number()
        track_code = generate_tracking_code()

        order = Order.objects.create(
            order_number=order_num,
            tracking_code=track_code,
            user=request.user if request.user.is_authenticated else None,
            customer_name=name,
            customer_email=email,
            customer_phone=phone,
            shipping_address=address,
            city=city,
            postal_code=postal_code,
            country=country,
            subtotal=subtotal,
            shipping_cost=shipping,
            discount_amount=discount,
            total_amount=total,
            payment_method=payment_method,
            payment_status='PAID' if payment_method in ['CARD', 'APPLE_PAY'] else 'PENDING',
            status='PLACED',
            estimated_delivery=(timezone.now() + timedelta(days=2)).strftime("%A, %b %d, %Y"),
        )

        # Create Order Items and adjust stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                shoe=item.shoe,
                size=item.size,
                quantity=item.quantity,
                unit_price=item.shoe.price
            )
            # decrement stock safely
            shoe_size = ShoeSize.objects.filter(shoe=item.shoe, size=item.size).first()
            if shoe_size and shoe_size.stock_quantity >= item.quantity:
                shoe_size.stock_quantity -= item.quantity
                shoe_size.save(update_fields=['stock_quantity'])

        # Initial Tracking Updates
        TrackingUpdate.objects.create(
            order=order,
            status_title="Order Confirmed & Placed",
            location="SoleStride Central Operations, Newark Hub",
            is_completed=True,
            description=f"Payment verified via {payment_method}. Automated invoice generated and forwarded to robotics sorting line."
        )
        TrackingUpdate.objects.create(
            order=order,
            status_title="Precision Quality Check",
            location="Inspection Station Bay #4",
            is_completed=False,
            description="Our footwear master specialists verify stitching, cushioning seal, and packaging integrity."
        )

        # Clear cart & coupon
        cart.items.all().delete()
        if 'coupon_code' in request.session:
            del request.session['coupon_code']

        messages.success(request, f"Order #{order_num} placed successfully! Tracking code: {track_code}")
        return redirect('order_success', tracking_code=track_code)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'shop/checkout.html', context)


def order_success_view(request, tracking_code):
    order = get_object_or_404(Order.objects.prefetch_related('items__shoe', 'timeline'), tracking_code=tracking_code)
    return render(request, 'shop/order_success.html', {'order': order})


def track_order_view(request):
    """
    Live Order & Delivery Tracking Page: Visual timeline, stages, courier info.
    """
    query = request.GET.get('code', '').strip()
    order = None
    recent_user_orders = Order.objects.none()

    if request.user.is_authenticated:
        recent_user_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]

    if query:
        order = Order.objects.filter(
            Q(tracking_code__iexact=query) | Q(order_number__iexact=query)
        ).prefetch_related('items__shoe', 'timeline').first()
        if not order:
            messages.error(request, f"No shipment found matching tracking code or order '{query}'. Please check and try again.")
    elif recent_user_orders.exists():
        # default to latest order if user is logged in
        order = recent_user_orders.first()

    context = {
        'order': order,
        'query': query,
        'recent_user_orders': recent_user_orders,
    }
    return render(request, 'shop/track_order.html', context)


def helpline_view(request):
    """
    Helpline, 24/7 Support, Live FAQ, Contact & Ticket submission.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        order_num = request.POST.get('order_number', '').strip()
        issue_type = request.POST.get('issue_type', 'TRACKING')
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and subject and message:
            import random
            ticket_id = f"TKT-{random.randint(10000, 99999)}"
            SupportTicket.objects.create(
                ticket_id=ticket_id,
                name=name,
                email=email,
                order_number=order_num,
                issue_type=issue_type,
                subject=subject,
                message=message
            )
            messages.success(request, f"Support ticket #{ticket_id} created! Our shoe specialists will reply within 2 hours.")
            return redirect('helpline')
        else:
            messages.error(request, "Please fill in all required ticket fields.")

    return render(request, 'shop/helpline.html')


def about_view(request):
    """
    About Us: Brand history, craftsmanship, sustainable lab, warranty standards.
    """
    return render(request, 'shop/about.html')


# --- AUTHENTICATION VIEWS ---

def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not (username and email and password):
            messages.error(request, "Username, email, and password are required.")
            return render(request, 'shop/register.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'shop/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return render(request, 'shop/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, f"An account with email '{email}' already exists.")
            return render(request, 'shop/register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        login(request, user)
        messages.success(request, f"Welcome to SoleStride, {user.first_name or user.username}!")
        return redirect('profile')

    return render(request, 'shop/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Sync any items from session cart
            get_or_create_cart(request)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or 'profile'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'shop/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('home')


@login_required(login_url='login')
def profile_view(request):
    """
    User Account Dashboard: order history with live delivery status badges.
    """
    user_orders = Order.objects.filter(user=request.user).prefetch_related('items__shoe').order_by('-created_at')
    context = {
        'user': request.user,
        'orders': user_orders,
        'orders_count': user_orders.count(),
    }
    return render(request, 'shop/profile.html', context)


@require_POST
def add_review_view(request, slug):
    shoe = get_object_or_404(Shoe, slug=slug)
    user_name = request.POST.get('user_name', 'Verified Shopper').strip()
    headline = request.POST.get('headline', 'Superb Comfort').strip()
    comment = request.POST.get('comment', '').strip()
    rating = int(request.POST.get('rating', 5))

    if comment:
        ShoeReview.objects.create(
            shoe=shoe,
            user=request.user if request.user.is_authenticated else None,
            user_name=request.user.get_full_name() or request.user.username if request.user.is_authenticated else user_name,
            rating=rating,
            headline=headline,
            comment=comment,
            verified_purchase=True
        )
        # Update shoe rating average
        avg = shoe.reviews.all().aggregate(Avg('rating'))['rating__avg']
        if avg:
            shoe.rating = round(avg, 1)
            shoe.review_count = shoe.reviews.count()
            shoe.save(update_fields=['rating', 'review_count'])
        messages.success(request, "Thank you! Your shoe review has been posted.")
    return redirect('shoe_detail', slug=slug)


# --- REST API VIEWS FOR DYNAMIC FRONTEND / HIGH CONCURRENCY ---

@require_GET
def api_shoe_list(request):
    """
    Fast JSON API for shoe catalog with query filtering.
    """
    shoes = Shoe.objects.select_related('brand', 'category').filter(in_stock=True)
    
    category = request.GET.get('category')
    if category:
        shoes = shoes.filter(category__slug=category)

    search = request.GET.get('q')
    if search:
        shoes = shoes.filter(Q(title__icontains=search) | Q(brand__name__icontains=search))

    serializer = ShoeSerializer(shoes[:30], many=True)
    return JsonResponse({'status': 'success', 'count': len(serializer.data), 'shoes': serializer.data})


@require_GET
def api_track_order(request, tracking_code):
    """
    JSON API for real-time delivery status tracking.
    """
    order = Order.objects.filter(
        Q(tracking_code__iexact=tracking_code) | Q(order_number__iexact=tracking_code)
    ).prefetch_related('items__shoe', 'timeline').first()

    if not order:
        return JsonResponse({'status': 'error', 'message': 'Tracking code not found'}, status=404)

    serializer = OrderTrackingSerializer(order)
    return JsonResponse({'status': 'success', 'order': serializer.data})


@require_POST
def api_cart_add(request):
    """
    AJAX endpoint for instant Add to Cart without full page reload.
    """
    try:
        import json
        data = json.loads(request.body) if request.body else request.POST
        shoe_id = data.get('shoe_id')
        size = data.get('size', '9.5')
        quantity = int(data.get('quantity', 1))

        shoe = get_object_or_404(Shoe, id=shoe_id)
        cart = get_or_create_cart(request)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            shoe=shoe,
            size=size,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save(update_fields=['quantity'])

        return JsonResponse({
            'status': 'success',
            'message': f"Added '{shoe.title}' (US {size}) to your bag!",
            'cart_count': cart.total_items,
            'subtotal': str(cart.subtotal),
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def api_cart_update(request):
    """
    AJAX endpoint for updating quantity or removing cart items.
    """
    try:
        import json
        data = json.loads(request.body) if request.body else request.POST
        item_id = data.get('item_id')
        action = data.get('action') # 'increase', 'decrease', 'remove'

        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save(update_fields=['quantity'])
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save(update_fields=['quantity'])
            else:
                cart_item.delete()
        elif action == 'remove':
            cart_item.delete()

        subtotal = cart.subtotal
        return JsonResponse({
            'status': 'success',
            'cart_count': cart.total_items,
            'subtotal': str(subtotal),
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_GET
def api_cart_status(request):
    cart = get_or_create_cart(request)
    items = []
    for it in cart.items.select_related('shoe').all():
        items.append({
            'id': it.id,
            'title': it.shoe.title,
            'size': it.size,
            'quantity': it.quantity,
            'price': str(it.shoe.price),
            'image': it.shoe.get_image_url,
            'subtotal': str(it.subtotal)
        })
    return JsonResponse({
        'count': cart.total_items,
        'subtotal': str(cart.subtotal),
        'items': items
    })
