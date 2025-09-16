from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import CheckoutFeedback
# Create your views here.
def index(request):
    template_data = {}
    template_data['title'] = 'Movies Store'
    return render(request, 'home/index.html', {'template_data': template_data})


def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request,
                  'home/about.html',
                  {'template_data': template_data})


def feedback_list(request):
    items = CheckoutFeedback.objects.all()
    template_data = {
        'title': 'Checkout Feedback',
        'items': items,
    }
    return render(request, 'home/feedback_list.html', {'template_data': template_data})

@require_POST
def feedback_submit(request):
    name = (request.POST.get('name') or '').strip()
    message = (request.POST.get('message') or '').strip()

    if message:
        CheckoutFeedback.objects.create(name=name, message=message)
        messages.success(request, "Thanks for the feedback!")
    else:
        messages.info(request, "Feedback cancelled or empty.")

    return redirect('home.feedback_list')