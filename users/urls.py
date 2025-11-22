from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.decorators.cache import cache_page

from users.apps import UsersConfig
from users.services import block_user, email_verification
from users.views import (CustomLoginView, EmailConfirmationView,
                         PasswordRecoveryView, RegisterView,
                         UserProfileDetailView, UserProfileUpdateView,
                         UsersListView)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "login/",
        CustomLoginView.as_view(
            template_name="users/login.html", next_page="newsletter:home"
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="newsletter:home"), name="logout"),
    path("list", cache_page(60)(UsersListView.as_view()), name="users_list"),
    path("block_user/<int:pk>", block_user, name="block_user"),
    path("email_confirm/<str:token>/", email_verification, name="email_confirm"),
    path(
        "email_confirmation/",
        EmailConfirmationView.as_view(),
        name="email_confirmation",
    ),
    path(
        "password_recovery/", PasswordRecoveryView.as_view(), name="password_recovery"
    ),
    path("profile/detail/", UserProfileDetailView.as_view(), name="profile_detail"),
    path("profile/update/", UserProfileUpdateView.as_view(), name="profile_update"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
