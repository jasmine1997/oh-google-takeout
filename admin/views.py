import os
import yaml
from django.apps import apps
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from app.decorators import admin_required


def log_in(request):
    if request.method == 'POST':
        if request.POST.get('admin_password') == os.getenv('ADMIN_PASSWORD'):
            login(request, User.objects.get(username='admin'))
            return redirect('admin_config')
        else:
            messages.error(request, 'Incorrect password')
            return redirect('admin_login')

    return render(request, 'admin_login.html')


@admin_required
def config(request):
    mode = 'w+' if request.method == 'POST' else 'r'
    f = open(os.path.join(apps.get_app_config('admin').path, 'defaults.yml'), mode)
    defaults = yaml.load(f) or {}
    if request.method == 'POST':
        defaults['file'] = {
            'name': request.POST['file_name'],
            'description': request.POST['file_description'],
            'tags': sorted([x.strip()
                            for x in request.POST['file_tags'].split(',')])
        }
        yaml.dump(defaults, f)
        f.close()
        response = redirect('admin_config')
    else:
        response = render(request, 'admin_config.html', context={
            'defaults': defaults
        })
    f.close()
    return response
