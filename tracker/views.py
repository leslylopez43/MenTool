from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, TemplateView, View, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView, FormView
from .forms import MoodForm
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

from .forms import UserRegistrationForm, UserLoginForm

from .models import Mood


class HomeView(LoginRequiredMixin, ListView):
    model = Mood
    template_name = 'tracker/tracker_home.html'
    login_url = reverse_lazy('login')

    def get_queryset(self):
        queryset = Mood.objects.filter(user=self.request.user).order_by('-date')[:7][::-1]
        return queryset


class MoodView(LoginRequiredMixin, CreateView):
    template_name = 'tracker/tracker_mood.html'
    model = Mood
    success_url = reverse_lazy('home')
    form_class = MoodForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.date = timezone.now()
        # check if the same date already exists in the user records
        check_mood_date = Mood.objects.filter(user=self.request.user, date=timezone.now()).first()
        if check_mood_date:
            form.add_error(None, "A mood record already exists. Go modify it!")
            return self.form_invalid(form)
        
        messages.success(self.request, "A mood record is successfully saved!", extra_tags="alert alert-success alert-dismissible")
        return super().form_valid(form)


class MoodDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Mood
    template_name = 'tracker/tracker_mood_detail.html'

    def test_func(self):
        mood = self.get_object()
        return self.request.user == mood.user


class UpdateMoodView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mood
    template_name = 'tracker/tracker_mood.html'
    success_url = reverse_lazy('stats')
    form_class = MoodForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.date = timezone.now()
        messages.success(self.request, "Successfully updated your Mood!", extra_tags="alert alert-success alert-dismissible")
        return super().form_valid(form)

    def test_func(self):
        mood = self.get_object()
        return self.request.user == mood.user


class DeleteMoodView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Mood
    success_url = reverse_lazy('home')
    template_name = 'tracker/tracker_confirm_mood_delete.html'

    def test_func(self):
        mood = self.get_object()
        messages.success(self.request, "Your Mood has been deleted!", extra_tags="alert alert-success alert-dismissible")
        return self.request.user == mood.user


class StatsView(ListView):
    model = Mood
    template_name = 'tracker/tracker_stats.html'

    def get_queryset(self):
        queryset = Mood.objects.all().order_by('date').filter(
            user=self.request.user)
        return queryset


class LandingView(TemplateView):
    template_name = 'tracker/tracker_landing.html'


class AboutUsView(TemplateView):
    template_name = 'tracker/tracker_about_us.html'


class SignUpView(CreateView):
    template_name = 'tracker/tracker_sign_up.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "You have been logged out!", extra_tags="alert alert-success alert-dismissible")
        return redirect(reverse_lazy("landing"))


class LoginView(FormView):
    template_name = 'tracker/tracker_login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        login(self.request, form.get_user())
        messages.success(self.request, "You have been logged in!", extra_tags="alert alert-success alert-dismissible")
        return super().form_valid(form)


class DeleteAccontView(LoginRequiredMixin, DeleteView):
    model = get_user_model()
    success_url = reverse_lazy('home')
    template_name = 'tracker/tracker_account_delete.html'

    def get_object(self, queryset=None):
        return self.request.user

