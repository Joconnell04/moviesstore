from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required
from django.urls import reverse

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())

    # If cart is empty, try to show the last order confirmation (after redirect)
    if movie_ids == []:
        last_order_id = request.session.get('last_order_id')
        if last_order_id:
            # One-time use, then clear the marker
            request.session.pop('last_order_id', None)
            template_data = {
                'title': 'Purchase confirmation',
                'order_id': last_order_id,
                # Script also checks for ?feedback=1 but this keeps behavior consistent
                'show_feedback_modal': True,
            }
            return render(request, 'cart/purchase.html', {'template_data': template_data})
        return redirect('cart.index')

    # Proceed with creating the order
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order(user=request.user, total=cart_total)
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()
    # Clear cart and redirect to self with feedback flag, carrying order_id in session
    request.session['cart'] = {}
    request.session['last_order_id'] = order.id
    return redirect(f"{reverse('cart.purchase')}?feedback=1")

def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html', {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')
