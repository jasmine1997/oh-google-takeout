from functools import wraps
from django.shortcuts import redirect

from application.models import Member


def state_required(required_state):

    def decorator(func):

        @wraps(func)
        def wrapper(request, *args, **kwargs):
            current_state = None
            try:
                request.member = Member.objects.get(pk=request.session.get('uid'))
                current_state = 'member'
            except Member.DoesNotExist:
                current_state = 'anonymous'
            finally:
                if required_state == current_state:
                    return func(request, *args, **kwargs)
                else:
                    if required_state == 'member':
                        return redirect('authorize')
                    if required_state == 'anonymous':
                        return redirect('dashboard')
        return wrapper

    return decorator
