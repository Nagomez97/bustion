from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
import os, json

from django.views.decorators.csrf import csrf_exempt

from app.models import Project, Web, Finding, Fuzzer

import logging

from app.backend import database, fuzz

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


#####################
# Main functionality
#####################


# Render login HTML
def applogin(request):
    return render(request, 'bustion/login.html')

# Logout and render login HTML
def applogout(request):
	logout(request)
	return applogin(request)


# [POST] Authenticate user and login
def auth(request):

	if request.method =='POST':

		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('/bustion/home')

	return render(request, 'bustion/login.html', {'status': False})


# [AUTH] Home
def home(request, errorMessage=None):
	if request.user.is_authenticated:
		username = request.user.username
		projects = database.getProjects()
		jobs = fuzz.getRunningJobs()
		return render(request, 'bustion/home.html', {'username': username, 'projects':projects, 'errorMessage': errorMessage, 'jobs': jobs})

	else:
		return redirect('/bustion/login')



#####################
# Project management
#####################

def viewProject(request, errorMessage=None):
	if request.method == 'GET' and request.user.is_authenticated:
		
		pid = request.GET['pid']

		if pid is not None:
			info = database.getProjectInfo(pid)
			jobs = fuzz.getRunningJobs()
			if info:
				return render(request, 'bustion/project.html', {'jobs':jobs, 'info': info, 'username': request.user.username, 'errorMessage': errorMessage})
	
	
	return redirect('/bustion/home')



# [POST] create project
def createProject(request):
	if request.method =='POST' and request.user.is_authenticated:
		name = request.POST['name']

		if name is not None:
			if not database.createProject(name):
				return home(request, 'Could not create project.')
	
	
	return redirect('/bustion/home')


# [POST] delete project
def deleteProject(request):
	if request.method =='POST' and request.user.is_authenticated:
		pid = request.POST['project-id']

		if pid is not None:
			if not database.deleteProject(pid):
				return home(request, 'Could not delete project.')
	
	
	return redirect('/bustion/home')

#####################
# Fuzzers management
#####################

def viewFuzzers(request, errorMessage=None, pid=None):
	if request.user.is_authenticated:
		try:
			username = request.user.username
			if pid is None:
					if request.method == 'POST':
						pid = request.POST['pid']
					else:
						pid = request.GET['pid']
			fuzzers = database.getFuzzers(pid)
			project = database.getProjectInfo(pid)
			jobs = fuzz.getRunningJobs()
			return render(request, 'bustion/fuzzers.html', {'jobs': jobs, 'project': project, 'username': username, 'fuzzers':fuzzers, 'errorMessage': errorMessage})
		except Exception as e:
			logger.error('Error showing fuzzer. Exception: {}'.format(e))
			return home(request, 'Error showing fuzzers.')

	else:
		return redirect('/bustion/login')

def addFuzzer(request):
	if request.method =='POST' and request.user.is_authenticated:
		try:
			name = request.POST['name']
			threads = request.POST['threads']
			wordlist = request.POST['wordlist']
			ua = request.POST['ua']
			extensions = request.POST['extensions']
			codes = request.POST['codes']
			verb = request.POST['verb']
			pid = request.POST['pid']
			proxy = request.POST['proxy']

			# Check if wordlist exists
			if not os.path.isfile(wordlist):
				return viewFuzzers(request, 'The wordlist does not exist.', pid=pid)

			if not database.addFuzzer(pid, name, threads, wordlist, ua, extensions, codes, verb, proxy):
				return viewFuzzers(request, 'Could not create fuzzer.', pid=pid)

		except Exception as e:
			return redirect('/bustion/home') 
	
	
	return viewFuzzers(request, None, pid)

# [POST] delete project
def deleteFuzzer(request):
	if request.method =='POST' and request.user.is_authenticated:
		fid = request.POST['fuzzer-id']
		pid = request.POST['pid']

		if fid is not None:
			if not database.deleteFuzzer(fid):
				return home(request, 'Could not delete fuzzer.')
	
	
	return viewFuzzers(request, None, pid)


def updateFuzzer(request):
	if request.method =='POST' and request.user.is_authenticated:
		try:
			name = request.POST['name']
			threads = request.POST['threads']
			wordlist = request.POST['wordlist']
			ua = request.POST['ua']
			extensions = request.POST['extensions']
			codes = request.POST['codes']
			verb = request.POST['verb']
			fid = request.POST['fid']
			pid = request.POST['pid']
			proxy = request.POST['proxy']

			if not database.updateFuzzer(pid, fid, name, threads, wordlist, ua, extensions, codes, verb, proxy):
				return viewFuzzers(request, 'Could not update fuzzer.', pid)
			else:
				return viewFuzzers(request, None, pid)

		except Exception as e:
			return home(request, e)

		
	
	
	return home(request)





#####################
# Webs management
#####################

# [AUTH] Home
def viewWebs(request, errorMessage=None):
	if request.user.is_authenticated:
		try:
			if request.method == 'POST':
				pid = request.POST['pid']
			else:
				pid = request.GET['pid']
			username = request.user.username
			webs = database.getWebsFromPid(pid)
			project = database.getProjectInfo(pid)
			jobs = fuzz.getRunningJobs()
			return render(request, 'bustion/webs.html', {'jobs':jobs, 'project': project, 'username': username, 'webs':webs, 'errorMessage': errorMessage})

		except Exception as e:
			logger.error('Error showing webs. Exception: {}'.format(e))
			return home(request, 'Could not show webs.')

	else:
		return redirect('/bustion/login')

# [AUTH/POST] Adds a new web
def addWeb(request):
	if request.method =='POST' and request.user.is_authenticated:
		try:
			shortname = request.POST['shortname']
			url = request.POST['url']
			pid = request.POST['pid']

			if not database.addWeb(shortname, url, pid):
				return viewWebs(request, 'Could not create web.')

		except Exception as e:
			logger.error('Error creating web. Exception: {}'.format(e))
			return viewWebs(request, 'Could not create web.')
	
	
	return viewWebs(request)


def updateWeb(request):
	if request.method =='POST' and request.user.is_authenticated:
		try:
			shortname = request.POST['shortname']
			url = request.POST['url']
			pid = request.POST['pid']
			wid = request.POST['wid']

			if not database.updateWeb(shortname, url, pid, wid):
				return viewWebs(request, 'Could not create web.')

		except Exception as e:
			logger.error('Error creating web. Exception: {}'.format(e))
			return viewWebs(request, 'Could not create web.')
	
	
	return viewWebs(request)


# [POST] delete web
def deleteWeb(request):
	if request.method =='POST' and request.user.is_authenticated:
		pid = request.POST['pid']
		wid = request.POST['wid']

		if wid is not None:
			if not database.deleteWeb(wid):
				return home(request, 'Could not delete web.')
	
	
	return redirect('/bustion/projects/webs?pid={}'.format(pid))




#####################
# Findings management
#####################

def findings(request, errorMessage=None):
	if request.user.is_authenticated:
		try:
			if request.method == 'POST':
				wid = request.POST['wid']
			else:
				wid = request.GET['wid']
			username = request.user.username

			web = database.getWebInfo(wid)
			p_info = database.getProjectInfo(web.project_id)
			findings = database.getFindings(wid)
			jobs = fuzz.getRunningJobs()
			return render(request, 'bustion/findings.html', {'jobs':jobs, 'findings': findings,'web': web, 'project': p_info, 'username': username, 'errorMessage': errorMessage})

		except Exception as e:
			logger.error('Error showing findings. Exception: {}'.format(e))
			return redirect('/projects/webs?pid={}'.format(pid))

	else:
		return redirect('/bustion/login')


def findingInfo(request):
	if request.user.is_authenticated:
		try:
			fid = request.GET['fid']

			finding = database.getSingleFinding(fid)

			result = {
				'path': finding.path,
				'url': finding.url,
				'code': finding.code,
				'size': finding.size,
				'fid': fid,
				'wid': finding.web_id	
			}

			return HttpResponse(json.dumps(result), content_type="application/json")

		except Exception as e:
			logger.error('Error showing findings. Exception: {}'.format(e))
			return HttpResponse(json.dumps({}), content_type="application/json")

	else:
		return HttpResponse(json.dumps({}), content_type="application/json")	


def deleteFinding(request):
	if request.method =='POST' and request.user.is_authenticated:
		fid = request.POST['fid']

		if fid is not None:
			if not database.deleteFinding(fid):
				return HttpResponse(json.dumps({'status':'error'}), content_type="application/json")
		else:
			return HttpResponse(json.dumps({'status':'error'}), content_type="application/json")
	
	
	return HttpResponse(json.dumps({'status':'ok'}), content_type="application/json")	

def deleteAllFinding(request):
	if request.method =='POST' and request.user.is_authenticated:
		wid = request.POST['wid']

		if wid is not None:
			if not database.deleteAllFinding(wid):
				return HttpResponse(json.dumps({'status':'error'}), content_type="application/json")
	
	
	return HttpResponse(json.dumps({'status':'ok'}), content_type="application/json")

# [AUTH/POST] Adds a new web
def addFinding(request):
	if request.method =='POST' and request.user.is_authenticated:
		try:
			path = request.POST['path']
			url = request.POST['url']
			code = request.POST['code']
			pid = request.POST['pid']
			wid = request.POST['wid']

			if not database.addManualFinding(wid, path, url, code):
				return HttpResponse(json.dumps({'status':'error'}), content_type="application/json")

		except Exception as e:
			logger.error('Error creating finding. Exception: {}'.format(e))
			return HttpResponse(json.dumps({'status':'error'}), content_type="application/json")
	
	
	return HttpResponse(json.dumps({'status':'ok'}), content_type="application/json")


def updateFinding(request):
	if request.method =='POST' and request.user.is_authenticated:
		try:
			path = request.POST['path']
			url = request.POST['url']
			code = request.POST['code']
			fid = request.POST['fid']
			wid = request.POST['wid']

			if not database.updateFinding(wid, fid, path, url, code):
				return HttpResponse(json.dumps({'status':'error'}), content_type="application/json")

		except Exception as e:
			logger.error('Error updating finding. Exception: {}'.format(e))
			return HttpResponse(json.dumps({'status':'error'}), content_type="application/json")
	
	
	return HttpResponse(json.dumps({'status':'ok'}), content_type="application/json")



#####################
# Launch management
#####################

def launchManager(request, errorMessage=None):
	if request.user.is_authenticated:
		try:
			if request.method == 'POST':
				pid = request.POST['pid']
			else:
				pid = request.GET['pid']

			fuzz.checkStatus(pid)

			username = request.user.username
			webs = database.getWebsFromPid(pid)
			project = database.getProjectInfo(pid)
			fuzzers = database.getFuzzers(pid)
			jobs = fuzz.getRunningJobs()

			return render(request, 'bustion/launch.html', {'jobs':jobs, 'fuzzers': fuzzers, 'project': project, 'username': username, 'webs':webs, 'errorMessage': errorMessage})

		except Exception as e:
			logger.error('Error showing launch manager. Exception: {}'.format(e))
			return viewProject(request, 'Error loading launch manager.')

	else:
		return redirect('/bustion/login')


class LaunchWeb:
	def __init__(self, wid, web):
		self.wid = wid
		self.web = web
		self.url = web

def launch(request):
	if request.method =='POST' and request.user.is_authenticated:
		try:
			username = request.user.username

			pid = request.POST['pid']
			fuzzer_id = request.POST['fuzzer']
			wid = request.POST['wid']

			fuzzer = database.getFuzzer(fuzzer_id)


			w = database.getWebInfo(wid)
			web = LaunchWeb(wid, w.url)

			result = fuzz.launch(pid, web, fuzzer)

			if result == -1:
				return launchManager(request, 'Job already running on {}'.format(web.web))

			if not result:
				return launchManager(request, 'Launch error.')

			return launchManager(request)

		except Exception as e:
			logger.error('Launch error. Exception: {}'.format(e))
			return viewProject(request, 'Launch error.')

	else:
		return home(request)


def killJob(request):
	if request.method =='POST' and request.user.is_authenticated:
		try:
			wid = request.POST['wid']
			pid = request.POST['pid']

			web = database.getWebInfo(wid)

			if not fuzz.killJob(web, pid):
				logger.error('Error on killing job.')
				return launchManager(request, 'Error killing job.')

			return launchManager(request)



		except Exception as e:
			logger.error('Error on killing job. Exception: {}'.format(e))
			return launchManager(request, 'Error killing job.')

	else:
		return home(request)



#####################
# Server-side datatables
#####################


def getPagedFindings(request):
	try:
		wid = request.POST['wid']
		draw = int(request.POST['draw'])
		order_idx = int(request.POST['order[0][column]'])
		order_col = request.POST['columns[{}][name]'.format(order_idx)]
		order_dir = request.POST['order[0][dir]']
		start = int(request.POST['start'])
		length = int(request.POST['length'])
		search_term = request.POST['search[value]']

		result = database.getPagedFindings(wid, draw, order_col, order_dir, start, length, search_term)

		return HttpResponse(result, content_type="application/json")


	except Exception as e:
		logger.error('Error retrieving paged information. Exception: {}'.format(e))
		return HttpResponse(json.dumps({}), content_type="application/json")