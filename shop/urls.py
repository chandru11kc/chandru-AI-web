from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.home_view, name='home'),
    path('store/', views.store_view, name='store'),
    path('shop/', views.store_view, name='shop'), # user alias
    path('shoe/<slug:slug>/', views.shoe_detail_view, name='shoe_detail'),
    path('shoe/<slug:slug>/review/', views.add_review_view, name='add_review'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/coupon/', views.apply_coupon_view, name='apply_coupon'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/success/<str:tracking_code>/', views.order_success_view, name='order_success'),
    path('track/', views.track_order_view, name='track_order'),
    path('helpline/', views.helpline_view, name='helpline'),
    path('about/', views.about_view, name='about'),
    
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # REST APIs
    path('api/shoes/', views.api_shoe_list, name='api_shoe_list'),
    path('api/track/<str:tracking_code>/', views.api_track_order, name='api_track_order'),
    path('api/cart/add/', views.api_cart_add, name='api_cart_add'),
    path('api/cart/update/', views.api_cart_update, name='api_cart_update'),
    path('api/cart/status/', views.api_cart_status, name='api_cart_status'),
]
