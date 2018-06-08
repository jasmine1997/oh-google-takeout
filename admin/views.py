import os
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from admin.models import FileMetadata


def log_in(request):
    if request.method == 'POST':
        if request.POST.get('admin_password') == os.getenv('ADMIN_PASSWORD'):
            login(request, User.objects.get(username='admin'))
            return redirect('admin_config')
        else:
            messages.error(request, 'Incorrect password')
            return redirect('admin_login')

    return render(request, 'admin_login.html')


def config(request):
    return render(request, 'admin_config.html', context={
        'files': FileMetadata.objects.all()
    })


def add_file(request):
    FileMetadata.objects.create(
        name=request.POST.get('name'),
        description=request.POST.get('description'),
        tags=request.POST.get('tags').split(',')
    )
    return redirect('admin_config')


def delete_file(request, id):
    FileMetadata.objects.get(pk=id).delete()
    return redirect('admin_config')
