from django.urls import include, path


def test(request):
    return None


urlpatterns = [
    path('', test),
]
