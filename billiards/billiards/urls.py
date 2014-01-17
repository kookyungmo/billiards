from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.generic.base import RedirectView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('billiards.views.match',
    url(r'^match/(?P<matchid>\d+)/$', 'detail', name="match_detail"),
    url(r'^match/(?P<matchid>\d+)/enroll', 'enroll', name="match_enroll"),
#     url(r'^match$', 'index', name="match"),
    url(r'^match/(?P<view>\w+)/$', 'index', name="match_map"),
)

urlpatterns += patterns('billiards.views.poolroom',
    url(r'^poolroom/(?P<poolroomid>\d+)/more$', 'more', name="poolroom_moreinfo"),
    url(r'^poolroom/(?P<poolroomid>\d+)$', 'detail', name="poolroom_detail"),
    url(r'^poolroom/nearby$', 'nearby', name="poolroom_nearby"),
    url(r'^poolroom/nearby/(?P<lat>\d+.\d+),(?P<lng>\d+.\d+)/(?P<distance>\d+)', 'nearby', name="poolroom_nearby_point_distance"),
    url(r'^poolroom/update_baidu_location', 'updateBaiduLocation', name="poolroom_internal_update_baidu_location"),
)

urlpatterns += patterns('billiards.views.user.login',
    url(r'^user/login/(?P<site_name>\w+)','login_3rd', name='login_3rd'),
    url(r'^user/oauth/(?P<site_name>\w+)', 'callback', name="oauth_code"),
    url(r'^user/oautherror/$', 'oautherror', name='oautherror'),
    url(r'^user/logout/$', 'logout', name='user_logout'),
)

urlpatterns += patterns('billiards.views.user.manage',
    url(r'^user/completeInfo','completeInfo', name='completeInfo'),
)

urlpatterns += patterns('',
#    url(r'^$', RedirectView.as_view(url='match/map', permanent=False), name="home"),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('billiards.views.us',
    url(r'^about$','about', name='about'),
    url(r'^join$','join', name='join'),
    url(r'^contact$','contact',name='contact'),
    url(r'^partner$','partner',name='partner'),
    url(r'^$', 'home', name='home'),
)

urlpatterns += patterns('billiards.views.challenge',
    url(r'^challenge$', 'index', name='challenge_list'),
    url(r'^challenge/(?P<lat>\d+.\d+),(?P<lng>\d+.\d+)$', 'index', name='challenge_with_distance'),
    url(r'^challenge/(?P<challengeid>\d+)/apply$', 'applyChallenge', name='apply_challenge'),
)

urlpatterns += patterns('billiards.views.utility',
    url(r'^unsupportedbrowser$', 'unsupportedbrowser', name='unsupportedbrowser'),
)

urlpatterns += patterns('billiards.views.club',
    url(r'^club$', RedirectView.as_view(url='club/match', permanent=False), name='club_index'),
    url(r'^club/match$', 'match', name='club_match'),
    url(r'^club/match/add$', 'match_add', name='club_match_add'),
    url(r'^club/match/edit/(?P<matchid>\d+)$', 'match_edit', name='club_match_edit'),
    url(r'^club/match/(?P<matchid>\d+)/enrollinfo$', 'match_enroll', name='club_match_enroll'),
    url(r'^club/challenge', 'challenge', name='club_challenge'),
)

urlpatterns += staticfiles_urlpatterns()
handler403 = 'billiards.views.exceptions.handler403'
handler404 = 'billiards.views.exceptions.handler404'
handler500 = 'billiards.views.exceptions.handler500'
