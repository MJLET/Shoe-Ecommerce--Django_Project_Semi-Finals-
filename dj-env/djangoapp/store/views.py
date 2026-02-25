from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Product, ProductVariant, Order, OrderItem
from django.contrib.auth.forms import UserCreationForm

# --- AUTHENTICATION ---
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def login_success_redirect(request):
    if request.user.is_staff:
        return redirect('/admin/')
    return redirect('product_list')

# --- SHOP DISPLAY ---
@login_required
def product_list(request):
    products = Product.objects.all().prefetch_related('variants')
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

# --- SHOPPING CART ---
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
    return redirect('cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    total_price = 0
    for item in cart.values():
        item['subtotal'] = float(item['price']) * int(item['quantity'])
        total_price += item['subtotal']
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
    return redirect('cart_detail')

def remove_from_cart(request, variant_id):
    cart = request.session.get('cart', {})
    v_id = str(variant_id)
    if v_id in cart:
        del cart[v_id]
        request.session['cart'] = cart
    return redirect('cart_detail')

# --- CHECKOUT & SUCCESS ---
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('product_list')
    
    # 🗝️ Calculate total directly to prevent KeyError
    total_price = sum(float(item['price']) * int(item['quantity']) for item in cart.values())
    
    if request.method == 'POST':
        # 🗝️ This logic creates the Order record in the database
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get('name'), 
            address=request.POST.get('address'),
            email=request.POST.get('email'),
            total_price=total_price # Fixes TypeError
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

def about(request):
    return render(request, 'store/about.html')

def contact(request):
    if request.method == "POST":
        # In a real app, you'd save this data or send an email here.
        # For your project, we'll just redirect to the success screen.
        return redirect('contact_success')
    return render(request, 'store/contact.html')

def contact_success(request):
    return render(request, 'store/contact_success.html')