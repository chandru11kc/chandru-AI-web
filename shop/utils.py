import random
import string
from .models import Cart

def get_or_create_cart(request):
    """
    High-performance cart retrieval using session_key for guests or user id for authenticated accounts.
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Merge guest cart if user just logged in with existing session
        if request.session.session_key:
            guest_cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if guest_cart and guest_cart != cart:
                for item in guest_cart.items.all():
                    existing_item = cart.items.filter(shoe=item.shoe, size=item.size).first()
                    if existing_item:
                        existing_item.quantity += item.quantity
                        existing_item.save(update_fields=['quantity'])
                    else:
                        item.cart = cart
                        item.save(update_fields=['cart'])
                guest_cart.delete()
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart

def generate_tracking_code():
    chars = string.ascii_uppercase + string.digits
    part1 = "".join(random.choices(chars, k=4))
    part2 = "".join(random.choices(chars, k=4))
    return f"STRIDE-{part1}-{part2}"

def generate_order_number():
    number = random.randint(100000, 999999)
    return f"SO-{number}"
