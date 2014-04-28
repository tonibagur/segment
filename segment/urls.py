from django.conf.urls import patterns, include, url
from segment.views import home
from segment.views import LImages, SegmentImage,EditImage,EditSegment
from django.contrib import admin
from django.contrib.auth.views import login
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'segment.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', login_required(home,login_url='/accounts/login/'), name='home'),
    url(r'^limages/',login_required(LImages.as_view(),login_url='/accounts/login/'),name='limages' ),
    url(r'^segment_image/',login_required(SegmentImage.as_view(),login_url='/accounts/login/'),name='segment_image' ),
    url(r'^edit_image/',login_required(EditImage.as_view(),login_url='/accounts/login/'),name='edit_image' ),
    url(r'^edit_segment/',login_required(EditSegment.as_view(),login_url='/accounts/login/'),name='edit_segment' ),
    url(r'^admin/', include(admin.site.urls)),


    url('^accounts/', include('django.contrib.auth.urls')),
    url('^register/', CreateView.as_view(
            template_name='register.html',
            form_class=UserCreationForm,
            success_url='/'
    )),
   # url(r'^accounts/register/$', '',{'template_name': 'register.html'}),



)
