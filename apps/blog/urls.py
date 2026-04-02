from django.urls import path

from .views import blog, view_post


urlpatterns = [
    path("", blog, name="blog"),
    path("<slug:slug>/", view_post, name="view_post"),
]
