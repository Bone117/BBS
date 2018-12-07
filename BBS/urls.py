"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from blog import views
from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', views.login_user),
    url(r'^get_valid_code/', views.get_valid_code),
    url(r'^register/', views.register),
    url(r'^check_username/', views.check_username),
    url(r'^index/', views.index),
    url(r'^logout/', views.logout_user),
    url(r'^media/(?P<path>.*)',serve, {'document_root':settings.MEDIA_ROOT}),

    url(r'^diggit/$',views.diggit),
    url(r'^comment_submit/$',views.comment_submit),
    url(r'^backed/$',views.backed),
    url(r'^add_article/$',views.add_article),
    url(r'^upload_img/$',views.upload_img),
    url(r'^up_userinfo/$',views.up_userinfo),
    url(r'^up_article/(?P<id>\d+)',views.up_article),
    url(r'^get_article/(?P<id>\d+)',views.get_article),


    url(r'^(?P<username>[\w]+)/(?P<condition>tag|category|archive)/(?P<param>.*)', views.user_blog),
    url(r'^(?P<username>[\w]+)/article/(?P<id>\d+)$', views.article_detail),
    url(r'^(?P<username>[\w]+)/', views.user_blog),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
