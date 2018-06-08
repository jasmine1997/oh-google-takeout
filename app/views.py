import os
import arrow
import ohapi
from pprint import pprint
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse

from app.models import OpenHumansMember
from admin.models import FileMetadata


def info(request):
    return render(request, 'info.html')


def authorize(request):
    return redirect(ohapi.api.oauth2_auth_url(
        client_id=os.getenv('OHAPI_CLIENT_ID'),
        redirect_uri=request.build_absolute_uri(reverse('authenticate'))
    ))


def authenticate(request):
    res = ohapi.api.oauth2_token_exchange(
        client_id=os.getenv('OHAPI_CLIENT_ID'),
        client_secret=os.getenv('OHAPI_CLIENT_SECRET'),
        redirect_uri=request.build_absolute_uri(reverse('authenticate')),
        code=request.GET.get('code'),
    )

    oh_id = ohapi.api.exchange_oauth2_member(
        access_token=res['access_token']
    )['project_member_id']

    member = OpenHumansMember.objects.get_or_create(
        user=User.objects.get_or_create(username=oh_id)[0],
        oh_id=oh_id,
        defaults={
            'access_token': res['access_token'],
            'refresh_token': res['refresh_token'],
            'expiration_time': arrow.utcnow().shift(
                seconds=res['expires_in']
            ).datetime
        })[0]

    login(request, member.user)
    return redirect('dashboard')


def dashboard(request):
    files = ohapi.api.exchange_oauth2_member(
        access_token=request.user.oh_member.get_access_token()
    )['data']
    return render(request, 'dashboard.html', context={
        'files': files,
        'file_metadata': FileMetadata.objects.all()
    })


def upload(request):
    pprint(request.FILES)


def log_out(request):
    logout(request)
    return redirect('info')
