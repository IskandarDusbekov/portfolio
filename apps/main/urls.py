from django.urls import path

from .views import index, submit_contact


urlpatterns = [
    path("", index, name="index"),
    path("contact/", submit_contact, name="submit_contact"),
]
