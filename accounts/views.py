import us
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.shortcuts import render
from django.views.generic.edit import FormView
import sesame.utils
from .models import UserProfile


def send_login_email(user, *, domain, is_signup):
    login_url = sesame.utils.get_query_string(user)

    if is_signup:
        title = "Welcome to OpenPrecincts!"
    else:
        title = "Sign in to OpenPrecincts"

    body = render_to_string(
        "accounts/email_body.txt",
        {
            "user": user,
            "is_signup": is_signup,
            "domain": domain,
            "login_url": login_url,
            "expiry_minutes": int(settings.SESAME_MAX_AGE / 60),
        },
    )

    send_mail(title, body, settings.DEFAULT_FROM_EMAIL, [user.email])


class SignupForm(forms.Form):
    email = forms.EmailField(label="Email address")
    display_name = forms.CharField(max_length=30, label="What should we call you?")
    state = forms.ChoiceField(
        choices=[("", "------")]
        + [(s.abbr, s.name) for s in us.STATES]
        + [("PR", "Puerto Rico")],
        label="Your state",
    )
    about = forms.CharField(widget=forms.Textarea, label="About You")
    slack = forms.BooleanField(label="Invite me to Slack!", initial=True)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).count():
            raise forms.ValidationError("Email already in use.")
        return email


class LoginForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email=email).count():
            raise forms.ValidationError("No registered user with this email.")
        return email


class Signup(FormView):
    template_name = "accounts/signup.html"
    form_class = SignupForm
    success_url = "/"

    @transaction.atomic
    def form_valid(self, form):
        u = User.objects.create(
            username=form.cleaned_data["email"],
            email=form.cleaned_data["email"],
            first_name=form.cleaned_data["display_name"],
        )
        UserProfile.objects.create(
            user=u,
            state=form.cleaned_data["state"],
            about=form.cleaned_data["about"],
            slack=form.cleaned_data["slack"],
        )

        send_login_email(u, domain=self.request.build_absolute_uri("/"), is_signup=True)

        return render(
            self.request,
            "accounts/email_sent.html",
            {"user": u, "expiry_minutes": int(settings.SESAME_MAX_AGE / 60)},
        )


class Login(FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        # at this point we can be sure there is a user with this email
        u = User.objects.get(email=form.cleaned_data["email"])

        send_login_email(
            u, domain=self.request.build_absolute_uri("/"), is_signup=False
        )

        return render(
            self.request,
            "accounts/email_sent.html",
            {"user": u, "expiry_minutes": int(settings.SESAME_MAX_AGE / 60)},
        )


@login_required
def profile(request):
    return render(request, "accounts/profile.html", {})
