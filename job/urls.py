from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, google_oauth_view, request_password_reset, confirm_password_reset, JobListingViewSet, JobApplicationViewSet

router = DefaultRouter()
router.register(r'jobs', JobListingViewSet, basename='job')
router.register(r'applications', JobApplicationViewSet, basename='application')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # path('login/', LoginView.as_view(), name='login'),
    path('oauth/google/', google_oauth_view, name='google-oauth'),
    path('password-reset/', request_password_reset, name='request-password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', confirm_password_reset, name='confirm-password-reset'),
    path('', include(router.urls)),
    # path('', google_oauth_frontend, name='google_oauth_frontend'),
]

