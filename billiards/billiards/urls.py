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
    url(r'^activity/(?P<matchid>\d+)/$', 'activity', name="activity_detail"),
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
    url(r'^challenge/publish/(?P<lat>\d+.\d+),(?P<lng>\d+.\d+)/(?P<distance>\d+)', 'publish', name="challenge_publish"),
    url(r'^challenge/(?P<challengeid>\d+)$', 'detail', name='challenge_detail'),
)

urlpatterns += patterns('billiards.views.utility',
    url(r'^unsupportedbrowser$', 'unsupportedbrowser', name='unsupportedbrowser'),
    url(r'^coupon/(?P<couponid>\d+)$', 'coupon', name='coupontracker')
)

urlpatterns += patterns('billiards.views.club',
    url(r'^club/$', 'index', name='club_index'),
    url(r'^club$', 'index', name='club_index'),
    url(r'^club/match$', 'match', name='club_match'),
    url(r'^club/match/add$', 'match_add', name='club_match_add'),
    url(r'^club/match/(?P<matchid>\d+)/edit$', 'match_edit', name='club_match_edit'),
    url(r'^club/match/(?P<matchid>\d+)/enrollinfo$', 'match_enroll', name='club_match_enroll'),
    url(r'^club/challenge$', 'challenge', name='club_challenge'),
    url(r'^club/challenge/add$', 'challenge_add', name='club_challenge_add'),
    url(r'^club/challenge/(?P<challengeid>\d+)/edit$', 'challenge_edit', name='club_challenge_edit'),
    url(r'^club/challenge/(?P<challengeid>\d+)/enrollinfo$', 'challenge_enroll', name='club_challenge_enroll'),
    url(r'^club/challengeapp/(?P<appid>\d+)/accept$', 'challengeapp_accept', name='club_challengeapp_accept'),
    url(r'^club/challengeapp/(?P<appid>\d+)/reject$', 'challengeapp_reject', name='club_challengeapp_reject'),
    url(r'^club/activity$', 'activity', name='club_activity'),
    url(r'^club/activity/add$', 'activity_add', name='club_activity_add'),
    url(r'^club/activity/(?P<activityid>\d+)/edit/$', 'activity_edit', name='club_activity_edit'),
    url(r'^club/apply$', 'club_apply', name='club_apply'),
)

urlpatterns += patterns('billiards.views.wechat',
    url(r'^wechatkb$', 'weixin', name='weixin'),
    url(r'^wechat/report$', 'activity_report', name='wechat_activity_report'),
    url(r'^wechat/report/newuser$', 'activity_report_newuser', name='wechat_activity_report_newuser'),
    url(r'^wechat/report/message$', 'activity_report_message', name='wechat_activity_report_message'),
    url(r'^wechat/bj-university-association$', 'bj_university_association', name='wechat_bj_university_association'),
)

urlpatterns += patterns('billiards.views.event',
    url(r'^event/(?P<year>\d{4})/(?P<month>\d{02})/(?:(?P<titleabbrev>[\w-]+))?$', 'detail', name='event_year_month_name'),
)

urlpatterns += staticfiles_urlpatterns()
handler403 = 'billiards.views.exceptions.handler403'
handler404 = 'billiards.views.exceptions.handler404'
handler500 = 'billiards.views.exceptions.handler500'
