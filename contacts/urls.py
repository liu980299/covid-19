#  Copyright (c) 2020. @ Xiang Liu

from django.conf.urls import include,url
from contacts.views import *

urlpatterns = [
	url('^add_profile/$',add_profile),
	url('^set_profile/$',set_profile),
	url('^check_risk/$',check_risk),
	url('^update_contacts/$',update_contacts),
	url(r'^forms/$',
	    FormList.as_view(), name='form-list'),
	url(r'^forms/(?P<form_name>\w+)/$',
	    FormDetail.as_view(), name='form-detail'),
	url(r'^form/(?P<form_name>\w+)/$',
	    FormUpdate.as_view(), name='form-update'),
	url(r'^risks/$', RiskList.as_view(), name='risk-list'),
	url(r'risks/(?P<risk_name>\w+)/$',RiskDetail.as_view(), name='risk-detail'),
	url(r'^profiles/$',
	    ProfileList.as_view(), name='profile-list'),
	url(r'^profiles/(?P<profile_id>[0-9]+)/$',
	    ProfileDetail.as_view(), name='profile-detail'),

	url(r'^configs/$', ConfigList.as_view(), name='config-list'),
	url(r'configs/(?P<config_name>\w+)/$', ConfigDetail.as_view(), name='config-detail')
]
