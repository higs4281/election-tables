from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, include, url
from django.contrib import admin
from tables import views
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^elections/2014/tables/$', 'tables.views.tables'),
    url(r'^elections/2014/tables/print/$', 'tables.views.tables', {'prnt':True}),
    url(r'^elections/admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
