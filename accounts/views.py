from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render
from django.views.generic.edit import FormView
import sesame.utils
from core.utils import all_states
from .models import UserProfile


class SignupForm(forms.Form):
    display_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    state = forms.ChoiceField(
        choices=all_states()
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).count():
            raise forms.ValidationError("email already in use")
        return email


class LoginForm(forms.Form):
    email = forms.EmailField()


class Signup(FormView):
    template_name = 'accounts/signup.html'
    form_class = SignupForm
    success_url = '/'

    @transaction.atomic
    def form_valid(self, form):
        u = User.objects.create(username=form.cleaned_data['email'],
                                email=form.cleaned_data['email'],
                                first_name=form.cleaned_data['display_name'],
                                )
        UserProfile.objects.create(user=u, state=form.cleaned_data['state'])
        return super().form_valid(form)


class Login(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = '/'

    def form_valid(self, form):
        try:
            u = User.objects.get(email=form.cleaned_data["email"])
        except User.DoesNotExist:
            u = None

        if u:
            send_mail("OpenPrecincts Login",
                      "magic link: http://localhost:8000/" + sesame.utils.get_query_string(u),
                      "noreply@openprecincts.org",
                      [u.email]
                      )

        return render(self.request,
                      "accounts/email_sent.html",
                      {"user": u,
                       "expiry_minutes": int(settings.SESAME_MAX_AGE / 60),
                       }
                      )


def profile(request):
    return render(request, "accounts/profile.html", {})
