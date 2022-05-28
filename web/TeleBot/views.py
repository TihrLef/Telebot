from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from Projects.models import Project
from Users.models import User
from Reports.models import Report
from .forms import FilterForm
from fpdf import FPDF
from django.http import Http404
from django.views.generic.edit import CreateView, UpdateView
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.urls import reverse
import tempfile
from tempfile import TemporaryDirectory as td
from django.contrib.auth.mixins import AccessMixin
from threading import Thread
import time
from Users.forms import UserModelForm
from django.contrib.admin.views.decorators import staff_member_required


from django.db.models import Q

class OwnerOnlyMixin(AccessMixin):
    def handle_no_permission(self):
        return super().handle_no_permission()
    def dispatch(self, request, pk, *args, **kwargs):
        user_page = self.get_object()
        if request.user.telegram_id != user_page.telegram_id and not request.user.is_staff :
            return self.handle_no_permission()
        return super().dispatch(request, pk, *args, **kwargs)
	


import web.urls

class TempDir:
	def __init__(self):
		self.name = None
	def MakeDir(self, path = None, prefix = '', lifetime = 0):
		th = Thread(target = self.creation, args=(path, prefix, lifetime))
		th.start()
		while self.name is None:
			time.sleep(0.01)

	def creation(self, path = None, prefix = '', lifetime = 0):
		if path:
			tempfile.tempdir = path
		temp = td(prefix = prefix)
		self.name = str(temp.name)
		time.sleep(lifetime)

# РћС‚РІРµС‚ РЅР° РІС‹Р·РѕРІ РѕСЃРЅРѕРІРЅРѕРіРѕ СЃР°Р№С‚Р°
# РђРґСЂРµСЃ: /TeleBot
@user_passes_test(User.is_verified)
def index(request):
	return render(
		request,
		'index.html',
		context={},
	)

def available_reports(request):
	if(request.user.is_staff):
		return Report.objects.all()
	return Report.objects.filter(Q(user__exact = request.user.telegram_id) | 
							  Q(project__responsible_user__telegram_id__exact = request.user.telegram_id)).order_by('project')

def available_projects(request):
	if request.user.is_staff:
		return Project.objects.all()
	return request.user.project_set.all()

def available_users(request):
	if request.user.is_staff:
		return User.objects.all()
	users = User.objects.none()
	for project in available_projects(request):
			if(request.user.telegram_id == project.responsible_user.telegram_id):
				users = users | project.users.all()
	return users

def make_pdf(request, reports, path):
	temp = TempDir()
	temp.MakeDir(path = path, prefix = 'TempPdf', lifetime = 180)
	name = temp.name
	pdf = FPDF()
	pdf.add_page()
	pdf.add_font("Sans", style = "", fname = r"TeleBot/static/Fonts/OpenSans/OpenSans-Regular.ttf", uni=True)
	pdf.add_font("Sans", style = "B", fname = r"TeleBot/static/Fonts/OpenSans/OpenSans-Bold.ttf", uni=True)
	for report in reports:
		pdf.set_font("Sans", style = "B", size = 12)
		pdf.multi_cell(w = 200, h = 8, txt = 'Project name: ' + report.project.name, align = "L", ln = 1)
		pdf.multi_cell(w = 200, h = 8, txt = 'Week: ' + str(report.report_date), align = "L", ln = 1)
		pdf.multi_cell(w = 200, h = 8, txt = 'Last author: ' + report.user.username, align = "L", ln = 1)
		pdf.multi_cell(w = 200, h = 8, txt = 'Message:', align = "L", ln = 1)
		pdf.set_font("Sans", style = "", size = 12)
		pdf.multi_cell(w = 200, h = 8, txt = report.message, align = "L", ln = 1)
		pdf.multi_cell(w = 200, h = 10, txt = '\n', align = "L", ln = 1)
	pdf.output(name + r"/simple_demo" + str(request.user) + ".pdf", "F")
	return name

@user_passes_test(User.is_verified)
def report(request):
	reports = available_reports(request)
	error_message = ''
	
	form = FilterForm()
	if request.method == 'POST':
		form = FilterForm(request.POST)
		if(form.is_valid()):
			data = form.cleaned_data
			if(data['project']): 
				reports = reports.filter(project__id__in = data['project'])
			if(data['user']): 
				reports = reports.filter(user__telegram_id__in = data['user'])
			if(data['left_date']):
				reports = reports.exclude(report_date__lte = data['left_date'])
			if(data['right_date']):
				reports = reports.filter(report_date__lte = data['right_date'])
		else:
			error_message = 'incorrect input data'
			reports = []

	path = r"TeleBot/static"
	name = make_pdf(request, reports, path)
	
	projects = available_projects(request)
	users = available_users(request)
	if len(users) == 1:
		users.clear()
	if len(projects) == 1:
		projects.clear()
	print(form)
	return render(
		request,
		'Reports/reports_list.html',
		context = {'reports': reports,
			 'projects': projects,
			 'available_users': users,
			 'error_message': error_message,
			 'form': form,
			 'pdfname': name[len(path):] + r"/simple_demo" + str(request.user) + ".pdf"})
	

class UsersListView(generic.ListView):
	model = User

class UserDetailView(OwnerOnlyMixin, generic.DetailView):
	model = User

@user_passes_test(User.is_verified)	
def user_detail(request,pk):
	try:
		tele_id=User.objects.get(telegram_id=pk)
	except User.DoesNotExist:
		raise Http404("РўР°РєРѕРіРѕ РїРµСЂСЃРѕРЅР°Р¶Р° РЅРµ СЃСѓС‰РµСЃС‚РІСѓРµС‚!")
	
	return render(
		request,
		'user/user_detail.html',
		context={'user':tele_id,}
	)

@staff_member_required
def archive_user(request, pk):
	user = User.objects.get(pk = pk)
	if user.is_active:
		user.is_active = False
		user.role = "Archived"
	else:
		user.is_active = True
		if user.is_staff:
			user.role = "Administrator"
		else:
			user.role = "Verified"
	user.save()
	return redirect(reverse('user-detail', args=[pk]))
@staff_member_required
def user_role_change(request, pk):
    user = User.objects.get(pk = pk)
    print("anything")
    
    if request.method == "POST":
        user.role = request.POST['role']
        if user.role == "Administrator":
            user.is_staff=True
            user.is_active=True
        if user.role == "Verified":
            user.is_staff=False
            user.is_active=True
        if user.role == "Unverified":
            user.is_staff=False
            user.is_active=False
        #form = UserModelForm(request.POST)
        #if(form.is_valid()):
            #user.role = form.cleaned_data['role']
        user.save()
    return HttpResponseRedirect(reverse('user-detail', args=[user.pk]))
@staff_member_required
def user_list(request):
	user_list = User.objects.all
	if request.method == "POST":
		id_list = request.POST.getlist('boxes')
		if request.POST['action'] == "РЈРґР°Р»РёС‚СЊ":
			for user_id in id_list:
				try:
					User.objects.filter(pk=int(user_id)).delete()
				except User.DoesNotExist:
					pass
		else:
			for user_id in id_list:
				try:
					User.objects.filter(pk=int(user_id)).update(is_active=True)
				except User.DoesNotExist:
					pass
	return render(request, 'Users/user_list.html', {"user_list" : user_list})

@user_passes_test(User.is_verified)
def send_contact(request):
     name = request.POST.get("name")
     email = request.POST.get("email")
     subject = request.POST.get("subject")
     message = request.POST.get("message")
     send_mail("РќРѕРІРѕРµ СЃРѕРѕР±С‰РµРЅРёРµ", message, email, ["telebotsupp@yandex.ru"],
    html_message="<html> РќРѕРІРѕРµ СЃРѕРѕР±С‰РµРЅРёРµ СЃ СЃР°Р№С‚Р°<br>"
      "Р�РјСЏ:" + name + '<br>'
      "Email РїРѕС‡С‚Р°:" + email + '<br>'
      "РўРµРјР°:" + subject + '<br>'
       "РЎРѕРѕР±С‰РµРЅРёРµ:" + message + "<br>"
   "</html>")
     request.session['sendmessage'] = "РЎРѕРѕР±С‰РµРЅРёРµ Р±С‹Р»Рѕ РѕС‚РїСЂР°РІР»РµРЅРѕ"
     return HttpResponseRedirect('contact-page')

def contact_page(request):
    return render(request, "contact.html")