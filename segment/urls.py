from django.conf.urls import patterns, include, url
from segment.views import home
from segment.views import LImages, SegmentImage,EditImage,EditSegment,get_matlab_file,get_zip_file
from segment import views
from django.contrib import admin
from django.contrib.auth.views import login
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from segment.forms import UserCreateForm

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
    url(r'^edit_imagetype/',login_required(views.EditImageType.as_view(),login_url='/accounts/login/'),name='edit_imagetype' ),
    url(r'^get_matlab_file/$',login_required(get_matlab_file,login_url='/login/'),name='get_matlab_file'),
    url(r'^get_zip_file/$',login_required(get_zip_file,login_url='/login/'),name='get_zip_file'),
    url(r'^coneptum/admin/', include(admin.site.urls)),


    url('^accounts/', include('django.contrib.auth.urls')),
    url('^register/', CreateView.as_view(
            template_name='register.html',
            form_class=UserCreateForm,
            success_url='/'
    )),
    #Forgotten password:
    url(r'^accounts/password/reset/$', 'django.contrib.auth.views.password_reset', {'post_reset_redirect' : '/accounts/password/reset/done/','template_name': 'registration/password_reset.html'}),
    url(r'^accounts/password/reset/done/$', 'django.contrib.auth.views.password_reset_done',{'template_name': 'registration/password_done.html'}),
    url(r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'post_reset_redirect' : '/accounts/password/done/','template_name': 'registration/password_reset_confirm.html'}),
    url(r'^accounts/password/done/$', 'django.contrib.auth.views.password_reset_complete', {'template_name': 'registration/password_reset_complete.html'}),
   # url(r'^accounts/register/$', '',{'template_name': 'register.html'}),



)
