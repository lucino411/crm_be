from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .views import CustomLoginView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login-home'),
    path('logout/', LogoutView.as_view(), name='logout'),

]
