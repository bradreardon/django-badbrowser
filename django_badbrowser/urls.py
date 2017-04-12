from django.conf.urls import url

from django_badbrowser.views import ignore, unsupported

urlpatterns = [
    url(r"^$", unsupported, name="django-badbrowser-unsupported"),
    url(r"^ignore/$", ignore, name="django-badbrowser-ignore"),
]
