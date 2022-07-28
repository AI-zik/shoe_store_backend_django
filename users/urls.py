from django.urls import path

from shoes.views import UserCartView
from .views import UserChangePasswordView, UserRegisterView, UserTokenCreateView, UserDetailView, UserListView, UserUpdateView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path("", UserListView.as_view(), name='users'),
    path("<int:user_id>/", UserDetailView.as_view(), name='user'),
    path("register/", UserRegisterView.as_view(), name='register'),
    path("login/", UserTokenCreateView.as_view(), name='login'),
    path("login/refresh/", TokenRefreshView.as_view(), name='login_refresh'),
    path("<int:user_id>/update/", UserUpdateView.as_view(), name='update_user'),
    path("<int:user_id>/change-password/", UserChangePasswordView.as_view(), name='update_user_password'),
    path("<int:user_id>/cart/", UserCartView.as_view(), name='user_cart')
]

urlpatterns = format_suffix_patterns(urlpatterns)