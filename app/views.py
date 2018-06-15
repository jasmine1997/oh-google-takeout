import os
import json
import arrow
import ohapi
import requests
from pprint import pprint
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, reverse

# from admin.models import FileMetadata
from app.decorators import member_required
from app.models import OpenHumansMember, File


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


@member_required
def sync(request):

    File.objects.all().delete()

    files = ohapi.api.exchange_oauth2_member(
        access_token=request.user.oh_member.get_access_token()
    )['data']

    for file in files:
        pprint(file)
        File.objects.get_or_create(
            id=file['id'],
            defaults={
                'member': request.user.oh_member,
                'metadata': {
                    'name': file['metadata']['filename'],
                    'description': file['metadata']['description'],
                    'tags': sorted(file['metadata']['tags'])
                },
                'dump': requests.get(file['download_url']).json()
            }
        )

        return redirect('dashboard')


@member_required
def dashboard(request):
    return render(request, 'dashboard.html', context={
        'files': request.user.oh_member.file_set.all(),
    })


@member_required
def upload(request):

    file = request.FILES['file_json']
    metadata = {
        'filename': request.POST['file_name'],
        'description': request.POST['file_description'],
        'tags': request.POST['file_tags']
    }

    with open(os.path.join(settings.MEDIA_ROOT, metadata['filename']), 'w+') \
            as f:
        json.dump(file, f)

    r = ohapi.api.upload_aws(
        target_filepath=os.path.join(
            settings.MEDIA_ROOT, metadata['filename']
        ),
        metadata=metadata,
        access_token=request.user.oh_member.get_access_token(),
        project_member_id=request.user.oh_member.oh_id
    )

    os.remove(os.path.join(settings.MEDIA_ROOT, file.metadata['name']))

    File.objects.create(
        id=r['file_id'],
        member=request.user.oh_member,
        metadata=metadata,
        dump=json.load(file)
    )

    return redirect('dashboard')


@member_required
def visualize(request):
    # file = requests.get(request.POST['file_url']).json()
    # with open(os.path.join(settings.MEDIA_ROOT, 'location_history.json')) as f:
    #     data = json.load(f)
    pprint(request.POST)
    return render(request, 'visualize.html', context={
        'file': 'http://localhost:8080/location_history.json'
    })


@member_required
def delete(request, id):
    File.objects.get(pk=id).remove()
    return redirect('dashboard')


def log_out(request):
    logout(request)
    return redirect('info')
