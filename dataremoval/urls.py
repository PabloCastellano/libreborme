from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view()),
    path("search", views.dataremoval_search, name="datarem-search"),
]
