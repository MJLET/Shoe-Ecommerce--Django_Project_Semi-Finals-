from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('register/', views.register, name='register'),
    path('login-success/', views.login_success_redirect, name='login_success'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:variant_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('remove/<int:variant_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('download-receipt/<int:order_id>/', views.download_receipt, name='download_receipt'),
    path('logout/', views.custom_logout, name='logout'),
    path('about/', views.about, name='about'),
]