from django.urls import path
# from django.contrib.auth.views import LoginView
from .views import *

app_name = "myauth"
 
urlpatterns = [
    path("", index_view, name="index"),
    # path("login/",
    #      LoginView.as_view(template_name = "myauth/login.html",
    #                        next_page = reverse_lazy("myauth:index"),
    #                        redirect_authenticated_user=True
    #                        ),
    #      name="login"
    #      ),
    path("login/", MyLoginView.as_view(), name="login"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("register/", RegisterView.as_view(), name="register"),
    path("users/", UsersListView.as_view(),  name="users"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="about-user"),
    path("user-profile-update/<int:pk>/", ProfileUpdateView.as_view(), name="user-profile-update"),
    path("user-update/<int:pk>/", UserUpdateView.as_view(), name="user-update"),
    path("cookies/set/", set_cookies_view, name="cookies-set"),
    path("cookies/get/", get_cookies_view, name="cookies-get"),
    path("session/set/", set_session_view, name="session-set"),
    path("session/get/", get_session_view, name="session-get"),
    path("hello/", HelloView.as_view(), name="hello"),
]
