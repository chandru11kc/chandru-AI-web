from .utils import get_or_create_cart
from .models import Category, Brand

def shop_context(request):
    """
    Context processor injecting cart item count, categories, and brands to all templates.
    """
    try:
        cart = get_or_create_cart(request)
        cart_count = cart.total_items
        cart_subtotal = cart.subtotal
    except Exception:
        cart_count = 0
        cart_subtotal = 0

    return {
        'cart_count': cart_count,
        'cart_subtotal': cart_subtotal,
        'nav_categories': Category.objects.all()[:6],
        'nav_brands': Brand.objects.all()[:6],
    }
