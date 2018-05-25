import ohapi
from django.shortcuts import render, redirect, reverse


def home(request):
    return render(request, 'home.html')


def authorize(request):
    return redirect(ohapi.api.oauth2_auth_url(
        redirect_uri=request.build_absolute_uri(reverse('authenticate'))
    ))


def authenticate(request):
    return None
