from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.generic.base import RedirectView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('billiards.views.match',
    url(r'^match/(?P<matchid>\d+)/$', 'detail', name="match_detail"),
#     url(r'^match$', 'index', name="match"),
    url(r'^match/(?P<view>\w+)/$', 'index', name="match_map"),
)

urlpatterns += patterns('billiards.views.poolroom',
    url(r'^poolroom/(?P<poolroomid>\d+)/more$', 'more', name="poolroom_moreinfo"),
    url(r'^poolroom/(?P<poolroomid>\d+)$', 'detail', name="poolroom_detail"),
    url(r'^poolroom/nearby$', 'nearby', name="poolroom_nearby"),
    url(r'^poolroom/nearby/(?P<lat>\d+.\d+),(?P<lng>\d+.\d+)', 'nearby', name="poolroom_nearby_point"),
)

urlpatterns += patterns('billiards.views.user.login',
    url(r'^user/login/(?P<site_name>\w+)/$','login_3rd', name='login_3rd'),
    url(r'^user/oauth/(?P<site_name>\w+).*', 'callback', name="oauth_code"),
    url(r'^user/oautherror/$', 'oautherror', name='oautherror'),
    url(r'^user/logout/$', 'logout', name='user_logout'),
)

urlpatterns += patterns('',
    url(r'^$', RedirectView.as_view(url='match/map', permanent=False), name="home"),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('billiards.views.us',
    url(r'^about','about', name='about'),
    url(r'^join','join', name='join'),
    url(r'^contact','contact',name='contact'),
    url(r'^partner','partner',name='partner'),
)
urlpatterns += staticfiles_urlpatterns()
