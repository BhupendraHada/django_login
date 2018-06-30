from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    url(
        regex=r'^create/$',
        view=views.OTPCreateView.as_view(),
        name="create"
    ),
    url(
        regex=r'^forgot/$',
        view=views.OTPForgotCreateView.as_view(),
        name="forgot"
    ),
    url(
        regex=r'^verify/$',
        view=views.OTPDetail.as_view(),
        name="detail"
    ),

]

urlpatterns = format_suffix_patterns(urlpatterns)
