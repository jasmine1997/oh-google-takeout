import os
import arrow
import ohapi
from django.shortcuts import render, redirect, reverse

from application.models import Member
from utilities.decorators import state_required


@state_required('anonymous')
def home(request):
    return render(request, 'home.html')


@state_required('anonymous')
def authorize(request):
    return redirect(ohapi.api.oauth2_auth_url(
        client_id=os.getenv('OHAPI_CLIENT_ID'),
        redirect_uri=request.build_absolute_uri(reverse('authenticate'))
    ))


@state_required('anonymous')
def authenticate(request):
    res = ohapi.api.oauth2_token_exchange(
        client_id=os.getenv('OHAPI_CLIENT_ID'),
        client_secret=os.getenv('OHAPI_CLIENT_SECRET'),
        redirect_uri=request.build_absolute_uri(reverse('authenticate')),
        code=request.GET.get('code'),
    )
    member_id = ohapi.api.exchange_oauth2_member(
        access_token=res['access_token']
    )['project_member_id']
    member = Member.objects.get_or_create(id=member_id, defaults={
        'access_token': res['access_token'],
        'refresh_token': res['refresh_token'],
        'expiration_time': arrow.utcnow().shift(
            seconds=res['expires_in']
        ).datetime
    })[0]
    request.session['uid'] = member.id
    return redirect('dashboard')


@state_required('member')
def dashboard(request):
    return render(request, 'dashboard.html')


def sign_out(request):
    request.session.flush()
    return redirect('home')
