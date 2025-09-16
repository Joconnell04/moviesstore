from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path('feedback', views.feedback_list, name='home.feedback_list'),
    path('feedback/submit', views.feedback_submit, name='home.feedback_submit'),
    path('about', views.about, name='home.about'),
]
