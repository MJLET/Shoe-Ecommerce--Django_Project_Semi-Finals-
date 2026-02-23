from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Product, ProductVariant, Order, OrderItem

def product_list(request):
    products = Product.objects.all().prefetch_related('variants')
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

def add_to_cart(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart = request.session.get('cart', {})
    v_id = str(variant_id)
    if v_id in cart:
        cart[v_id]['quantity'] += 1
    else:
        cart[v_id] = {
            'name': variant.product.name,
            'color': variant.color_name,
            'price': str(variant.product.base_price),
            'image': variant.image.url if variant.image else '',
            'quantity': 1
        }
    request.session['cart'] = cart
    return redirect('cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
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

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart: return redirect('product_list')
    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=request.POST.get('full_name'), email=request.POST.get('email'),
            address=request.POST.get('address'), total_paid=total_price
        )
        for v_id, item in cart.items():
            variant = get_object_or_404(ProductVariant, id=v_id)
            OrderItem.objects.create(order=order, product_variant=variant, price=item['price'], quantity=item['quantity'])
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
    response['Content-Disposition'] = f'attachment; filename="Receipt_{order.id}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response