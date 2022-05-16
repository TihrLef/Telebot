from django.urls import path
from django.urls import re_path
import django
import Projects.views
from . import views
from .views import(contact_page, send_contact,)
from Projects.models import Project
from Users.models import User
from Reports.models import Report
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.views.static import serve
from web import settings


#Не трогайте эту строчку! Добавляйте новые ниже!
urlpatterns = []
#urlpatterns +=[re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),]
urlpatterns += [re_path(r'^static/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.STATIC_ROOT, 'show_indexes': settings.DEBUG})]
urlpatterns += [re_path(r'^project/(?P<pk>\d+)/change/$', Projects.views.project_change, name = "project-change")]
urlpatterns += [re_path(r'^$', views.index, name='index'),]
urlpatterns += [re_path(r'^users/$', views.user_list, name='users'),]
urlpatterns += [re_path(r'^projects/$', Projects.views.project_list, name='projects'),]
urlpatterns += [re_path(r'^project/(?P<pk>\d+)$', Projects.views.project_detail, name='project-detail'),]
urlpatterns += [re_path("success",  user_passes_test(User.is_verified)(TemplateView.as_view(template_name="success.html")), name="success"),]
urlpatterns += [re_path(r'^user/(?P<pk>\d+)$',  user_passes_test(User.is_verified)(views.UserDetailView.as_view()), name='user-detail') ]
urlpatterns += [re_path(r'^reports/$', views.report, name = "reports")]
urlpatterns += [re_path(r'^help/$', views.make_pdf, name = "maker_pdf")]
urlpatterns += [re_path(r'^projects/create$',  Projects.views.project_add, name = "project-create")]
urlpatterns += [re_path(r'^project/(?P<pk>\d+)/change/$', Projects.views.project_change, name = "project-change")]
urlpatterns += [re_path(r'^contact-page/$', contact_page), ]
urlpatterns += [re_path(r'^contact-page/send-contact/$', send_contact), ]
#urlpatterns += [re_path(r'^requests/$', staff_member_required(views.admin_approval), name='unver_users')]
