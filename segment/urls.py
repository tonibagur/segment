from django.conf.urls import patterns, include, url
from segment.views import home
from segment.views import LImages, SegmentImage,EditImage,EditSegment
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'segment.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', home, name='home'),
    url(r'^limages/',LImages.as_view(),name='limages' ),
    url(r'^segment_image/',SegmentImage.as_view(),name='segment_image' ),
    url(r'^edit_image/',EditImage.as_view(),name='edit_image' ),
    url(r'^edit_segment/',EditSegment.as_view(),name='edit_segment' ),
    url(r'^admin/', include(admin.site.urls)),
)
