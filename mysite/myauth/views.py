from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _, ngettext
from django.views.generic import View, TemplateView, CreateView, ListView, DetailView, UpdateView
from .models import Profile, User


# Create your views here.

class HelloView(View):
    welcome_message = _("Нello world!")
    
    def get(self, request):
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h2>"
        )

class AboutMeView(TemplateView):
    
    template_name = "myauth/about-me.html"

    def post(self, request, *args, **kwargs):
        context = {}
        context["upload_result"], context["permisson"] = manage_avatar(request.user, request)
        return render(request, self.template_name, context=context)


class RegisterView(CreateView):
    
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")

        user = authenticate(
            self.request,
            username=username,
            password=password,
            )
        login(request=self.request, user=user)
        return response


class UsersListView(ListView):

    template_name = "myauth/users-list.html"
    queryset = User.objects.select_related("profile")
    context_object_name = "users"
    http_method_names = "get"


class UserDetailView(DetailView):

    template_name = "myauth/about-user.html"
    queryset = User.objects.select_related("profile")
    context_object_name = "selected_user"
    http_method_names = "get", "post"

    def post(self, request, *args, **kwargs):
        
        object = self.get_object()
        context = {"selected_user": object}
        user = request.user
        if user.is_staff or user.pk == object.pk:
            context["upload_result"], context["permission"] = manage_avatar(object, request)
        else:
            context["permission"] = False
        return render(request, self.template_name, context=context)


class UserUpdateView(PermissionRequiredMixin, UpdateView):

    template_name = "myauth/user-update.html"
    queryset = User.objects.select_related("profile")
    fields = "first_name", "last_name", "email"
    context_object_name = "user"
    http_method_names = "get", "post"
    permission_required = []

    def get_success_url(self) -> str:
        return reverse_lazy(
            "myauth:about-user",
            kwargs={"pk": self.object.pk},
        )

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        if request.user.is_staff or request.user.pk == object.pk:
            return super().get(request, *args, **kwargs)
        else:
            return self.handle_no_permission()
  
    def post(self, request, *args, **kwargs):
        object = self.get_object()
        if request.user.is_staff or request.user.pk == object.pk:
            return super().post(request, *args, **kwargs)
        else:
            return self.handle_no_permission()


class ProfileUpdateView(PermissionRequiredMixin, UpdateView):

    template_name = "myauth/user-profile-update.html"
    queryset = Profile.objects.select_related("user")
    fields = "avatar", "bio", "agreement_accepted"
    context_object_name = "profile"
    http_method_names = "get", "post"
    permission_required = []

    def get_success_url(self) -> str:
        return reverse_lazy(
            "myauth:about-user",
            kwargs={"pk": self.object.user.pk},
        )
        
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        if request.user.is_staff or request.user.pk == object.user.pk:
            return super().get(request, *args, **kwargs)
        else:
            return self.handle_no_permission()
  
    def post(self, request, *args, **kwargs):
        object = self.get_object()
        form = self.get_form()
        if request.user.is_staff or request.user.pk == object.user.pk:
            if form.is_valid():                    
                return super().post(request, *args, **kwargs)
            else:
                return self.get(request, *args, **kwargs)
        else:
            return self.handle_no_permission()
        

class MyLoginView(LoginView):

    template_name = "myauth/login.html"
    next_page = reverse_lazy("myauth:about-me")
    redirect_authenticated_user=True


class MyLogoutView(LogoutView):
    
    template_name = "myauth/logout.html"
    http_method_names = ["post", "get", "options"]
    next_page = reverse_lazy("myauth:index")


def index_view(request: HttpRequest) -> HttpResponse:
    return render(request, "myauth/index.html")

def get_cookies_view(request: HttpRequest) -> HttpResponse:
    cookie_value = request.COOKIES.get("my_cookie", "default_cookie")
    return HttpResponse(f"Считано Cookie: {cookie_value!r}")

def set_cookies_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Установлено Cookie")
    response.set_cookie("my_cookie", "my_cookie1", max_age=3000)
    return response

def get_session_view(request: HttpRequest) -> HttpResponse:
    session_value = request.session.get("my_session", "не установлена")
    return HttpResponse(f"Сессия: {session_value!r}")

def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["my_session"] = "Новая сессия"
    return HttpResponse("Сессия установлена")

#--------------------------------------------------------------------------------

def manage_avatar(user, request):
    newfile = request.FILES.get("avatar")
    if newfile:
        if newfile.size > 51200:
            result = "Размер файла не должен превышать 50 кБ", True
        else:
            if  not Profile.objects.filter(user=user).exists(): # если профиль для пользователя не создан,
                Profile.objects.create(user=user)               # создать профиль для пользователя
                user.refresh_from_db()                          # обновить объект пользователя из БД
            user.profile.avatar.save(newfile, newfile)          # сохранить аватар в профиле (имя, содержимое)
            result = "Аватар {} успешно загружен".format(newfile), False
        return result
    else:
        return "Аватар не загружен", True
