from django.urls import path
from . import views

urlpatterns = [
    path('shortenurl/', views.get_short_url, name='get_short_url'),
]