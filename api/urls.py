from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import UserViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')


from django.urls import include

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserViewSet.as_view({'post': 'create'}), name='register'),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    path('reset-password/', UserViewSet.as_view({'post': 'reset_password'}), name='reset-password'),
    path('verify-otp/', UserViewSet.as_view({'post': 'verify_otp'}), name='verify-otp'),
    path('set-password/', UserViewSet.as_view({'post': 'set_password'}), name='set-password'),
    path('forgot-password/', UserViewSet.as_view({'post': 'forgot_password'}), name='forgot-password'),
]
