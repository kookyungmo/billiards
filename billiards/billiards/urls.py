from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

UUID_PATTERN = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

urlpatterns = patterns('billiards.views.match',
    url(r'^match/(?P<matchid>\d+)/$', 'detail', name="match_detail"),
    url(r'^match/(?P<matchid>\d+)/enroll', 'enroll', name="match_enroll"),
#     url(r'^match$', 'index', name="match"),
    url(r'^match/(?P<view>\w+)/$', 'index', name="match_map"),
    url(r'^activity/(?P<matchid>\d+)/$', 'activity', name="activity_detail"),
    url(r'^match/redbull/2014/05', 'redbull_2014_05', name='match_redbull_2014_05'),
    url(r'^match/redbull/winners', 'winners', name='winners'),
    url(r'^qcodes', 'qcodes', name='qcodes'),
)

urlpatterns += patterns('billiards.views.poolroom',
    url(r'^poolroom/(?P<poolroomid>\d+)/more$', 'more', name="poolroom_moreinfo"),
    url(r'^poolroom/(?P<poolroomid>\d+)$', 'detail', name="poolroom_detail"),
    url(r'^poolroom/(?P<poolroom_uuid>%s)/more$' %(UUID_PATTERN), 'more_uuid', name="poolroom_moreinfo_uuid"),
    url(r'^poolroom/(?P<poolroom_uuid>%s)$' %(UUID_PATTERN), 'detail_uuid', name="poolroom_detail_uuid"),
    url(r'^poolroom/nearby$', 'nearby', name="poolroom_nearby"),
    url(r'^poolroom/nearby/(?P<lat>\d+.\d+),(?P<lng>\d+.\d+)/(?P<distance>\d+)', 'nearby', name="poolroom_nearby_point_distance"),
    url(r'^poolroom/update_baidu_location', 'updateBaiduLocation', name="poolroom_internal_update_baidu_location"),
    url(r'^poolroom/query/keyword/(?P<keyword>[\w\W ]+)', 'query', name='query_by_keyword'),
)

urlpatterns += patterns('billiards.views.user.login',
    url(r'^user/login/(?P<site_name>\w+)','login_3rd', name='login_3rd'),
    url(r'^user/oauth/(?P<site_name>\w+)', 'callback', name="oauth_code"),
    url(r'^user/oautherror/$', 'oautherror', name='oautherror'),
    url(r'^user/logout/$', 'logout', name='user_logout'),
    url(r'^user/login','login_3rd_page', name='login_3rd_page'),
)

urlpatterns += patterns('billiards.views.user.manage',
    url(r'^user/completeInfo','completeInfo', name='completeInfo'),
    url(r'^user/(?P<wechatid>\w+)/membership/(?P<group>\d+)/apply', 'membership_apply', name='membership_apply'),
    url(r'^user/(?P<wechatid>\w+)/membership/(?P<group>\d+)$', 'membership', name='membership'),
    url(r'^sohucs/info', 'sohucs_getinfo', name='sohucs_getinfo'),
    url(r'^sohucs/login', 'sohucs_login', name='sohucs_login'),
    url(r'^sohucs/logout', 'sohucs_logout', name='sohucs_logout'),
    url(r'^sohucs/waplogin', 'sohucs_waplogin', name='sohucs_waplogin'),
)

urlpatterns += patterns('',
#    url(r'^$', RedirectView.as_view(url='match/map', permanent=False), name="home"),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^supadmin/', include(admin.site.urls)),
)

urlpatterns += patterns('billiards.views.us',
    url(r'^about$','about', name='about'),
    url(r'^join$','join', name='join'),
    url(r'^contact$','contact',name='contact'),
    url(r'^partner$','partner',name='partner'),
    url(r'^$', 'home', name='home'),
    url(r'^home1$', 'home1', name='home1'),
    url(r'^pictureservice$','pictureservice', name='pictureservice'),
)

urlpatterns += patterns('billiards.views.lottery',
    url(r'^lottery$','lottery', name='lottery'),
)

urlpatterns += patterns('billiards.views.2048',
    url(r'^redbull2048$','game_2048',name='game_2048'),
)

urlpatterns += patterns('billiards.views.challenge',
    url(r'^challenge/(?:(?P<group>\d+)/)?(?P<lat>\d+.\d+),(?P<lng>\d+.\d+)$', 'index', name='challenge_with_distance'),
    url(r'^challenge/(?P<challengeid>\d+)/apply$', 'applyChallenge', name='apply_challenge'),
    url(r'^challenge/publish/(?:(?P<group>\d+)/)?(?P<lat>\d+.\d+),(?P<lng>\d+.\d+)/(?P<distance>\d+)', 'publish', name="challenge_publish"),
    url(r'^challenge/(?P<challengeid>\d+)$', 'detail', name='challenge_detail'),
    url(r'^challenge/group/(?P<group>\d+)$', 'index', name='challenge_group_list'),
    url(r'^challenge$', 'index', name='challenge_list'),
    url(r'^challenge/wechatpublish', 'wechatpublish', name="challenge_wechatpublish"),
    url(r'^challenge/(?P<uuid>%s)$' %(UUID_PATTERN), 'detail_uuid', name="challenge_detail_uuid"),
    url(r'^challenge/(?P<uuid>%s)/apply$' %(UUID_PATTERN), 'apply_uuid', name='apply_challenge_uuid'),
)

urlpatterns += patterns('billiards.views.utility',
    url(r'^unsupportedbrowser$', 'unsupportedbrowser', name='unsupportedbrowser'),
    url(r'^coupon/(?P<couponid>\d+)$', 'coupon', name='coupontracker'),
    url(r'^wechatshare', 'wechatsharehelp', name='wechat_share_help'),
    url(r'^survey/redbull', 'survey_redbull', name='survey_redbull_2014_04'),
    url(r'^pkmap/(?P<mtype>\w+)/(?P<tid>\d+|%s)$' %(UUID_PATTERN), 'pkmap', name='pk_map_type_id'),
    url(r'^pkmap$', 'pkmap', name='pk_map'),
    url(r'^wechat/alipay', 'wechat_alipay', name='wechat_alipay')
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
    url(r'^wechatkb/strongworld$', 'wechat', name='wechat'),
    url(r'^wechat/report$', 'activity_report', name='wechat_activity_report'),
    url(r'^wechat/report/newuser$', 'activity_report_newuser', name='wechat_activity_report_newuser'),
    url(r'^wechat/report/message$', 'activity_report_message', name='wechat_activity_report_message'),
)

urlpatterns += patterns('billiards.views.wechatpartner',
     url(r'^wechat/bj-university-association$', 'bj_university_association', name='wechat_bj_university_association'),
     url(r'^wechat/bj_dabenying$', 'bj_dabenying', name='wechat_bj_dabenying'),
)

urlpatterns += patterns('billiards.views.event',
    url(r'^event/(?P<year>\d{4})/(?P<month>\d{02})/(?:(?P<titleabbrev>[\w-]+))?$', 'detail', name='event_year_month_name'),
)

urlpatterns += patterns('billiards.views.trade',
     url(r'^trade/membership$', 'membership', name='trade_membership'),
)

urlpatterns += patterns('billiards.views.transaction',
     url(r'^transaction/goods/(?P<sku>\w{32})$', 'pay_goods', name='transaction_pay_goods'),
)

urlpatterns += patterns('billiards.pay',
     url(r'^transaction/alipay/return$', 'b_alipay.alipay_return', name='transaction_alipay_return'),
     url(r'^transaction/alipay/wap/return$', 'b_alipay.alipay_wapreturn', name='transaction_alipay_wapreturn'),
     url(r'^transaction/alipay/wap/notify$', 'b_alipay.alipay_wapnotify', name='transaction_alipay_wapnotify'),
     url(r'^transaction/alipay/notify$', 'b_alipay.alipay_notify', name='transaction_alipay_notify'),
     url(r'^transaction/nowpay/notify$', 'nowpay.pay_notify', name='transaction_nowpay_notify'),
     url(r'^transaction/nowpay/return$', 'nowpay.pay_return', name='transaction_nowpay_return'),
)

urlpatterns += patterns('billiards.views.games',
    url(r'^2048$','game_2048', name='game_2048'),
)

urlpatterns += patterns('billiards.views.assistant',
    url(r'^assistant/static/(?P<resource_name>\w+).html','static_resouce', name='assistant_static_resouce'),
    url(r'^assistant/list$','assistant_list', name='assistant_list'),
    url(r'^assistant/(?P<assistant_uuid>%s)/offer/booking$' %(UUID_PATTERN),'assistant_offer_booking_by_uuid', name='assistant_offer_book'),
    url(r'^assistant/(?P<assistant_uuid>%s)/offer$' %(UUID_PATTERN),'assistant_offer_by_uuid', name='assistant_offer'),
    url(r'^assistant/(?P<assistant_uuid>%s)/like$' %(UUID_PATTERN),'assistant_like_by_uuid', name='assistant_like'),
    url(r'^assistant/(?P<assistant_uuid>%s)/unlike$' %(UUID_PATTERN),'assistant_unlike_by_uuid', name='assistant_unlike'),
    url(r'^assistant/(?P<assistant_uuid>%s)/stats$' %(UUID_PATTERN),'assistant_stats_by_uuid', name='assistant_stats'),
    url(r'^assistant/(?P<assistant_uuid>%s)/orders$' %(UUID_PATTERN),'assistant_orders_by_uuid', name='assistant_orders'),
    url(r'^assistant/(?P<assistant_uuid>%s)/order/(?P<transaction_id>\d{1,})$' %(UUID_PATTERN),'assistant_order_complete_by_tid', name='assistant_order_complete'),
    url(r'^assistant/(?P<assistant_uuid>%s)$' %(UUID_PATTERN),'assistant_by_uuid', name='assistant_detail'),
    url(r'^user/order$', 'user_assistant_order', name='user_assistant_order'),
    url(r'^assistant/order/\w{8}(?P<order_id>\d{8})/cancel', 'order_cancel', name='assistant_order_cancel'),
    url(r'^assistant/order/\w{8}(?P<order_id>\d{8})', 'order_detail', name='assistant_order_detail'),
    url(r'^assistant$','assistant', name='assistant'),
)

urlpatterns += staticfiles_urlpatterns()
handler403 = 'billiards.views.exceptions.handler403'
handler404 = 'billiards.views.exceptions.handler404'
handler500 = 'billiards.views.exceptions.handler500'
