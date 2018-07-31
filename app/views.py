import os
import json
import yaml
import arrow
import ohapi
import requests
from django.apps import apps
from django.conf import settings
from urllib.parse import parse_qs
from django.http import HttpResponse
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
    return redirect(reverse('dashboard') + '?modal=true')


@member_required
def sync(request):

    File.objects.all().delete()

    files = ohapi.api.exchange_oauth2_member(
        access_token=request.user.oh_member.get_access_token()
    )['data']

    for file in files:
        File.objects.create(
            id=file['id'],
            member=request.user.oh_member,
            metadata={
                'name': file['metadata']['filename'],
                'description': file['metadata']['description'],
                'tags': file['metadata']['tags']
            },
            dump=requests.get(file['download_url']).json()
        )

    return redirect('dashboard')


@member_required
def dashboard(request):
    with open(os.path.join(apps.get_app_config('admin').path, 'defaults.yml'), 'r') as f:
        defaults = yaml.load(f)
    return render(request, 'dashboard.html', context={
        'files': request.user.oh_member.file_set.all(),
        'defaults': defaults
    })


@member_required
def upload(request):

    file = request.FILES['file_json']
    metadata = {
        'filename': request.POST['file_name'],
        'description': request.POST['file_description'],
        'tags': sorted([x.strip() for x in
                        request.POST['file_tags'].split(',')])
    }

    file_path = os.path.join(settings.MEDIA_ROOT, metadata['filename'])

    with open(file_path, 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)

    r = ohapi.api.upload_aws(
        target_filepath=file_path,
        metadata=metadata,
        access_token=request.user.oh_member.get_access_token(),
        project_member_id=request.user.oh_member.oh_id
    )

    params = parse_qs(r.request.body)

    with open(file_path, 'r') as f:
        File.objects.create(
            id=int(params['file_id'][0]),
            member=request.user.oh_member,
            metadata=metadata,
            dump=json.load(f)
        )

    os.remove(file_path)

    return redirect('dashboard')


@member_required
def download(request, id):

    file = File.objects.get(pk=id)
    result = file.dump
    date_range = request.GET.get('date_range')
    if date_range is not None:
        date_range = date_range.split(' - ')
        (l, r) = [arrow.get(d) for d in date_range]
        result['locations'] = [
            x for x in file.dump['locations']
            if l <= arrow.get(int(x['timestampMs']) * .001) <= r
        ]

    res = HttpResponse(json.dumps(result),
                       content_type='application/json')
    res['Content-Disposition'] = 'attachment; filename={}' \
        .format(file.metadata['filename'])
    return res


@member_required
def visualize(request, id):

    file = File.objects.get(pk=id)
    dates = [
        arrow.get(
            int(file.dump['locations'][x]['timestampMs']) * 0.001
        ).format() for x in [-1, 0]
    ]

    return render(request, 'visualize.html', context={
        'file_id': id,
        'params': request.GET.dict(),
        'dates': dates
    })


@member_required
def delete(request, id):
    File.objects.get(pk=id).remove()
    return redirect('dashboard')


def log_out(request):
    logout(request)
    return redirect('info')
