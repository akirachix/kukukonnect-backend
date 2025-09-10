from django.urls import path
from .views import APIRootView, ThresholdView
from .views import SignupView, LoginView, ResetPasswordView, VerifyCodeView, ForgotPasswordView, SetPasswordView, UserAPIView, UserDetailView

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('users/', UserAPIView.as_view(), name='users'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('register/', SignupView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('verify-otp/', VerifyCodeView.as_view(), name='verify-otp'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('thresholds/<str:mcu_device_id>/', ThresholdView.as_view(), name='thresholds-detail'),
]
