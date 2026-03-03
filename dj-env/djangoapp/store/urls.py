# store/urls.py

from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),

    # Shop Display
    path('shop/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Shopping Cart - 🗝️ ONLY ONE CART PATH
    path('cart/', views.cart_detail, name='cart'), 
    path('add/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:variant_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('remove/<int:variant_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('download-receipt/<int:order_id>/', views.download_receipt, name='download_receipt'),

    # Info Pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
]