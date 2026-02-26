# store/context_processors.py

def cart_count(request):
    """Calculates total items in the cart to show the badge."""
    # Get cart from session, default to empty dict
    cart = request.session.get('cart', {})
    
    # Calculate the total number of items
    total_items = sum(int(item.get('quantity', 0)) for item in cart.values())
    
    return {'cart_total_items': total_items}