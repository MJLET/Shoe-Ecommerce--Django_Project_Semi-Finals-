from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib import messages
from django.utils import timezone
from xhtml2pdf import pisa
import datetime

from .models import Product, ProductVariant, Order, OrderItem
from django.contrib.auth.forms import UserCreationForm

# --- 1. AUTHENTICATION & SECURITY ---
# store/views.py

# store/views.py

# store/views.py

def register(request):
    registration_error = False
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 🗝️ Add a specific success message for the Home page popup
            messages.success(request, f"Registration successful! Welcome to StepUp, {user.username}.")
            login(request, user)
            
            # 🗝️ CHANGE: Redirect to 'home' instead of 'product_list'
            return redirect('home') 
        else:
            registration_error = True
    else:
        form = UserCreationForm()
        
    return render(request, 'registration/register.html', {
        'form': form, 
        'registration_error': registration_error
    })
# --- 1. AUTHENTICATION & SECURITY ---

def login_view(request):
    # ... existing session check ...
    last_attempt = request.session.get('last_attempt_time')
    
    # 🗝️ CHANGE: Lock after 3 attempts, shorten wait to 30s
    if request.session.get('login_attempts', 0) >= 3 and last_attempt:
        last_time = datetime.datetime.fromisoformat(last_attempt)
        wait_time = (timezone.now() - last_time).total_seconds()
        
        if wait_time < 30: # 🗝️ Changed from 60 to 30
            remaining = int(30 - wait_time)
            # 🗝️ Pass 'remaining' as a variable so JavaScript can see it
            return render(request, 'registration/login.html', {'remaining': remaining})
        else:
            request.session['login_attempts'] = 0

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            request.session['login_attempts'] = 0
            login(request, user)
            return redirect('product_list')
        else:
            request.session['login_attempts'] += 1
            request.session['last_attempt_time'] = timezone.now().isoformat()
            attempts_left = 3 - request.session['login_attempts']
            
            # 🗝️ ISSUE FIX: Identify the error and the field it belongs to
            error_msg = ""
            if attempts_left > 0:
                error_msg = f"Invalid login. {attempts_left} left."
            else:
                error_msg = "Account locked for 60s."
            
            # 🗝️ Pass 'error_field' so the template knows to highlight the password box
            return render(request, 'registration/login.html', {
                'error_message': error_msg,
                'error_field': 'password'
            })

    return render(request, 'registration/login.html')

def custom_logout(request):
    logout(request)
    return redirect('login')

# store/views.py

def home(request):
    # 🗝️ Fetch the latest 3 products to show on the Home page
    featured_products = Product.objects.all().prefetch_related('variants')[:3]
    
    return render(request, 'store/home.html', {
        'featured_products': featured_products
    })

# --- 2. SHOP DISPLAY ---

@login_required
def product_list(request):
    products = Product.objects.all().prefetch_related('variants')
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

# --- 3. SHOPPING CART ---

# --- 3. SHOPPING CART (Fixed Redirects & Clear Cart) ---

# --- 3. SHOPPING CART (Fixed Redirects & Clear Cart) ---

def add_to_cart(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart = request.session.get('cart', {})
    v_id = str(variant_id)
    
    cart[v_id] = {
        'name': variant.product.name,
        'color': variant.color_name,
        'price': str(variant.product.base_price),
        'image': variant.image.url if variant.image else '',
        'quantity': cart.get(v_id, {}).get('quantity', 0) + 1
    }
    request.session['cart'] = cart
    # 🗝️ FIX: Redirect to 'cart', not 'cart_detail'
    return redirect('cart')

def cart_detail(request):
    cart = request.session.get('cart', {})
    total_price = sum(float(item['price']) * int(item['quantity']) for item in cart.values())
    
    for item in cart.values():
        item['subtotal'] = float(item['price']) * int(item['quantity'])
        
    return render(request, 'store/cart.html', {'cart': cart, 'total_price': total_price})

def update_cart(request, variant_id, action):
    cart = request.session.get('cart', {})
    v_id = str(variant_id)
    if v_id in cart:
        if action == 'increase':
            cart[v_id]['quantity'] += 1
        elif action == 'decrease' and cart[v_id]['quantity'] > 1:
            cart[v_id]['quantity'] -= 1
        request.session['cart'] = cart
    # 🗝️ FIX: Redirect to 'cart'
    return redirect('cart')

def remove_from_cart(request, variant_id):
    cart = request.session.get('cart', {})
    v_id = str(variant_id)
    if v_id in cart:
        del cart[v_id]
        request.session['cart'] = cart
    # 🗝️ FIX: Redirect to 'cart'
    return redirect('cart')

# 🗝️ NEW FEATURE: Clear the entire bag
def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart')
# --- 4. CHECKOUT & ORDERS ---

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('product_list')
    
    total_price = sum(float(item['price']) * int(item['quantity']) for item in cart.values())
    
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get('name'), 
            address=request.POST.get('address'),
            email=request.POST.get('email'),
            total_price=total_price
        )

        for v_id, item_data in cart.items():
            OrderItem.objects.create(
                order=order,
                product_name=item_data['name'],
                color=item_data['color'],
                price=item_data['price'],
                quantity=item_data['quantity']
            )

        request.session['cart'] = {}
        return redirect('order_success', order_id=order.id)
    
    return render(request, 'store/checkout.html', {'total_price': total_price, 'cart': cart})

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_success.html', {'order': order})

def download_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    template = get_template('store/receipt_pdf.html')
    html = template.render({'order': order})
    response = HttpResponse(content_type='application/pdf')
    pisa.CreatePDF(html, dest=response)
    return response

# --- 5. STATIC PAGES ---

def about(request):
    return render(request, 'store/about.html')

def contact(request):
    if request.method == "POST":
        messages.success(request, "Your message has been sent. We'll get back to you soon!")
        return redirect('contact_success')
    return render(request, 'store/contact.html')

def contact_success(request):
    return render(request, 'store/contact_success.html')