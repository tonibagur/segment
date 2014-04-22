from django.conf.urls import patterns, include, url
from segment.views import home
from segment.views import LImages
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'segment.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', home, name='home'),
    url(r'^limages/',LImages.as_view(),name='limages' ),
    url(r'^admin/', include(admin.site.urls)),
)
