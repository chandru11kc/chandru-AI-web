import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solestride.settings')
django.setup()

from shop.models import Shoe

def test_routes():
    c = Client()
    endpoints = [
        ('/', 200, "Home page"),
        ('/store/', 200, "Store catalog"),
        ('/shop/', 200, "Shop alias"),
        ('/shoe/nexus-turbo-react-x1/', 200, "Shoe detail page"),
        ('/cart/', 200, "Cart page"),
        ('/track/', 200, "Track order search page"),
        ('/track/?code=STRIDE-8842-NY', 200, "Track order with code"),
        ('/helpline/', 200, "Helpline support page"),
        ('/about/', 200, "About us page"),
        ('/login/', 200, "Login page"),
        ('/register/', 200, "Register page"),
        ('/api/shoes/', 200, "REST API: Shoe list"),
        ('/api/track/STRIDE-8842-NY/', 200, "REST API: Order tracking"),
        ('/api/cart/status/', 200, "REST API: Cart status"),
    ]

    all_passed = True
    print("\n--- RUNNING ROUTE & API VERIFICATION ---")
    for url, expected_code, name in endpoints:
        res = c.get(url)
        status = "PASS" if res.status_code == expected_code else "FAIL"
        print(f"[{status}] {name} ({url}) -> HTTP {res.status_code}")
        if res.status_code != expected_code:
            all_passed = False

    print("\n--- TESTING AJAX CART ADD ---")
    shoe = Shoe.objects.first()
    cart_add_res = c.post(
        '/api/cart/add/',
        data=f'{{"shoe_id": {shoe.id}, "size": "10.0", "quantity": 1}}',
        content_type='application/json'
    )
    print(f"Cart Add Status: HTTP {cart_add_res.status_code}, Response: {cart_add_res.json()}")
    if cart_add_res.status_code != 200 or cart_add_res.json().get('status') != 'success':
        all_passed = False

    checkout_res = c.get('/checkout/')
    ch_status = "PASS" if checkout_res.status_code == 200 else "FAIL"
    print(f"[{ch_status}] Checkout page with items (/checkout/) -> HTTP {checkout_res.status_code}")
    if checkout_res.status_code != 200:
        all_passed = False

    if all_passed:
        print("\nALL SYSTEM TESTS PASSED SUCCESSFULLY! [OK]")
    else:
        print("\nSOME TESTS FAILED! [ERROR]")

if __name__ == '__main__':
    test_routes()
