from random import random

from django import forms
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from .models import Profile
from django.views import View
from .forms import UserAvatarForm, UserProfileForm
from django.utils.translation import gettext_lazy as _, ngettext_lazy
from django.views.decorators.cache import cache_page

class HelloView(View):
    welcome_message = _('Hello World!')
    def get(self, request: HttpRequest) -> HttpResponse:
        items_string = request.GET.get('items') or 0
        items = int(items_string)
        products_line = ngettext_lazy(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items_string)
        return HttpResponse(
            f'<h1>{self.welcome_message}</h1>'
            f'\n<h2>{products_line}</h1>'
                            )


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/admin')
        return render(request, 'myauth/login.html')

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin')

    return render(request, 'myauth/login.html', {'error': 'Invalid username or password.'})


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:login')


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse("myauth:login"))

@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response

@cache_page(60*2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "Default value")
    return HttpResponse(f'Cookie value: {value!r} + {random()}')


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spamegs"
    return HttpResponse('Session set')


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "Default value")
    return HttpResponse(f'Session value: {value!r}')

class ProfileCreateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        self.object = self.get_object()
        if self.request.user.is_staff:
            return True
        user_is_current_user = str(self.object.username) == str(self.request.user)
        return user_is_current_user
    model = User
    form_class = UserProfileForm
    template_name = 'myauth/user_profile_form.html'
    def get_success_url(self):
        return reverse(
            "myauth:about_me",
        )

class AvatarUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        self.object = self.get_object()
        if self.request.user.is_staff:
            return True
        user_is_current_user = str(self.object.user.username) == str(self.request.user)
        return user_is_current_user

    model = Profile
    form_class = UserAvatarForm
    template_name = 'myauth/user_avatar_form.html'
    def get_success_url(self):
        return reverse(
            "myauth:about_me",
        )


class AboutMeView(TemplateView):
    queryset = User.objects.prefetch_related('profile')
    context_object_name = 'user_'
    template_name = 'myauth/about-me.html'


class UserDetailView(DetailView):
    queryset = User.objects.prefetch_related('profile')
    context_object_name = 'user_'
    template_name = 'myauth/about-me.html'



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    bio = forms.CharField(widget=forms.Textarea)
    agreement_accepted = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        Profile.objects.create(user=user, bio=self.cleaned_data['bio'],
                               agreement_accepted=self.cleaned_data['agreement_accepted'])
        return user






class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about_me')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request,
                            username=username,
                            password=password)
        login(self.request, user)
        return response

class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'foo': 'bar', 'bar': 'baz'})


class UserListView(ListView):
    template_name = 'myauth/user_list.html'
    model = User
    context_object_name = 'users'

