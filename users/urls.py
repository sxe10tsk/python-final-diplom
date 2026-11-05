from django.urls import path
from .views import (
	RegisterView, RegisterConfirmView, LoginView, LogoutView, UserDetailsView,
	PasswordResetRequestView, PasswordResetConfirmView, ContactListCreateView, ContactDetailView,
)

urlpatterns = [
	path('user/register', RegisterView.as_view(), name='user-register'),
	path('user/register/confirm/<uidb64>/<token>', RegisterConfirmView.as_view(), name='user-register-confirm'),
	path('user/login', LoginView.as_view(), name='login'),
	path('user/logout', LogoutView.as_view(), name='logout'),
	path('user/details', UserDetailsView.as_view(), name='user_details'),
	path('user/password-reset', PasswordResetRequestView.as_view(), name='password_reset'),
	path('user/password-reset/confirm/<uidb64>/<token>', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
	path('user/contact', ContactListCreateView.as_view(), name='contact_list'),
	path('user/contact/<int:pk>', ContactDetailView.as_view(), name='contact_detail'),
]
