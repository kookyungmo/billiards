from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.generic.base import RedirectView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='match/map', permanent=False), name="home"),
    url(r'^match/(?P<matchid>[\d]+)', 'billiards.views.match.detail', name="match_detail"),
    url(r'^match$', 'billiards.views.match.index', name="match"),
    url(r'^match/?(?P<view>[\w]*)', 'billiards.views.match.index', name="match_map"),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
