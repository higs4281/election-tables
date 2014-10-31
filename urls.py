from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, include, url
from django.contrib import admin
from tables import views
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^elections/2014/tables/$', 'tables.views.tables'),
    url(r'^elections/2014/tables/counties/download/$', 'tables.views.counties'),
    url(r'^elections/2014/tables/counties/preview/$', 'tables.views.counties', {'preview': True}),
    url(r'^elections/admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
