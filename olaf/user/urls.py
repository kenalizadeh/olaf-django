from rest_framework_jwt.views import verify_jwt_token
from django.urls import path
from user.views import *

app_name = 'user'

urlpatterns = [
    path(r'authenticate_user', AuthenticateUser.as_view(), name='authenticate'),
    path(r'verify_token', verify_jwt_token, name='verify-token'),
    path(r'profile', UserProfileView.as_view(), name='profile'),
    path(r'request_tfa', PhoneNumberVerificationRequest.as_view(), name='request-tfa'),
    path(r'validate_tfa', TFACodeValidation.as_view(), name='validate-tfa'),
    path(r'merchant_login', MerchantLoginView.as_view(), name='merchant-login'),
    path(r'user_activity', UserActivityUpdateView.as_view(), name='activity'),
    path(r'footnotes/list', FootNoteListView.as_view(), name='footnote-list'),
    path(r'footnotes/<int:footnote_id>', FootNoteView.as_view(), name='footnote-detail'),
    path(r'footnotes/create', FootNoteCreateView.as_view(), name='footnote-create'),
    path(r'footnotes/test', FootNoteCreateTestView.as_view())
]