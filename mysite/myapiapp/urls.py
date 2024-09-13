from django.urls import path
from .views import hello_world,GroupsListView

app_name = 'myapiapp'

urlpatterns = [
    path('hello/', hello_world, name='hello'),
    path('groups/', GroupsListView.as_view(), name='GroupsListView'),
]