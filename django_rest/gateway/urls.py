from django.urls import path
from .views import LoginView, RegisterView, RefreshView, SecureView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('refresh/', RefreshView.as_view()),
    path('secure/', SecureView.as_view()),
]
