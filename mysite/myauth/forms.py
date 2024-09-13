from django import forms
from django.core import validators
from .models import Profile
from django.contrib.auth.models import Group, User


class UserAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "avatar",

class UserProfileForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea)
    agreement_accepted = forms.BooleanField(required=False)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        Profile.objects.create(user=user, bio=self.cleaned_data['bio'],
                               agreement_accepted=self.cleaned_data['agreement_accepted'],
                               avatar=self.cleaned_data['avatar'])
        return user
