from django.contrib.auth.views import LoginView
from django.urls import path
from .views import logout_view, MyLogoutView, set_cookie_view, get_cookie_view, set_session_view, get_session_view, \
    AboutMeView, RegisterView, FooBarView, AvatarUpdateView, ProfileCreateView, UserListView, UserDetailView, HelloView

app_name = 'myauth'
urlpatterns = [
    # path('login/', login_view, name='login'),
    path('login/',
         LoginView.as_view(
             template_name='myauth/login.html',
             redirect_authenticated_user=True,
         ),
         name='login'),

    path('hello/', HelloView.as_view(), name='hello'),
    path('logout/', logout_view, name='logout'),

    path('about-me/', AboutMeView.as_view(), name='about_me'),
    path('register/', RegisterView.as_view(), name='register'),

    path('cookie/get', get_cookie_view, name='cookie_get'),
    path('cookie/set', set_cookie_view, name='cookie_set'),

    path('session/get', get_session_view, name='session_get'),
    path('session/set', set_session_view, name='session_set'),


    path('foo-bar/', FooBarView.as_view(), name='foo-bar'),
    path('user-list/', UserListView.as_view(), name='user-list'),
    path("user-details/<int:pk>", UserDetailView.as_view(), name="user-details"),
    path("user-details/<int:pk>/update-profile/", ProfileCreateView.as_view(), name="create-profile"),

    path("user-details/<int:pk>/avatar/", AvatarUpdateView.as_view(), name="change-avatar"),


]
