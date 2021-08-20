from app.models import Project, Web, Finding, Fuzzer
import logging
from math import floor

from django.core.paginator import Paginator
import json

logger = logging.getLogger(__name__)

# Get all projects from DDBB
def getProjects():
	try:
		projects = Project.objects.all()
		return projects

	except Exception as e:
		logger.error('Error retrieving projects from database. {}'.format(e))
		return []

# Creates a new project
def createProject(name):
	try:
		p = Project(name=name)
		p.save()

		return True

	except Exception as e:
		logger.error('Error adding project to database. {}'.format(e))
		return False

# deletes a new project
def deleteProject(pid):
	try:
		Project.objects.filter(id=pid).delete()

		return True

	except Exception as e:
		logger.error('Error deleting project from database. {}'.format(e))
		return False


class ProjectInfo:

	pid = None
	project_name = None
	webs_num = None
	fuzzers_num = None
	findings_num = None

	def __init__(self, pid, name, webs, fuzzers, findings):

		self.pid = pid
		self.project_name = name
		self.webs_num = webs
		self.fuzzers_num = fuzzers
		self.findings_num = findings

# retrieves info from project
def getProjectInfo(pid):

	try: 
		project = Project.objects.get(id=pid)
		name = project.name
		webs = Web.objects.filter(project_id=pid)
		webs_count = webs.count()
		fuzzers = Fuzzer.objects.filter(project_id=pid).count()

		findings = 0

		for web in webs:
			findings += Finding.objects.filter(web_id=web.id).count()	

		return ProjectInfo(pid, name, webs_count, fuzzers, findings)

	except Exception as e:
		logger.error('Error retrieving project info. {}'.format(e))
		return None



##############################
# Fuzzers
##############################

def getFuzzers(pid):
	try:
		fuzzers = Fuzzer.objects.filter(project_id=pid)
		return fuzzers

	except Exception as e:
		logger.error('Error retrieving fuzzers from database. {}'.format(e))
		return []

def addFuzzer(pid, name, threads, wordlist, ua, extensions, codes, verb, proxy):
	try:
		p = Fuzzer(project_id=pid, name=name, threads=threads, wordlist=wordlist, user_agent=ua, extensions=extensions, hide_codes=codes, verb=verb, proxy=proxy)
		p.save()

		return True

	except Exception as e:
		logger.error('Error adding fuzzer to database. {}'.format(e))
		return False


def getFuzzer(fid):
	try:
		fuzzer = Fuzzer.objects.get(id=fid)
		return fuzzer

	except Exception as e:
		logger.error('Error retrieving fuzzer from database. {}'.format(e))
		return None

def updateFuzzer(pid, fid, name, threads, wordlist, ua, extensions, codes, verb, proxy):
	try:
		p = Fuzzer(project_id=pid, id=fid, name=name, threads=threads, wordlist=wordlist, user_agent=ua, extensions=extensions, hide_codes=codes, verb=verb, proxy=proxy)
		p.save()

		return True

	except Exception as e:
		logger.error('Error updating fuzzer from database. {}'.format(e))
		return False

# deletes a fuzzer
def deleteFuzzer(fid):
	try:
		Fuzzer.objects.filter(id=fid).delete()

		return True

	except Exception as e:
		logger.error('Error deleting fuzzer from database. {}'.format(e))
		return False



##############################
# Webs
##############################

def getWebsFromPid(pid):
	try:
		webs = Web.objects.filter(project_id=pid)
		for web in webs:
			web.findings = Finding.objects.filter(web_id=web.id).count()
		return webs

	except Exception as e:
		logger.error('Error retrieving webs from database. {}'.format(e))
		return []

def getRunningWebs(pid):
	try:
		webs = Web.objects.filter(project_id=pid, fuzzer_status="RUNNING")
		return webs

	except Exception as e:
		logger.error('Error retrieving pending webs from database. {}'.format(e))
		return []


def addWeb(shortname, url, pid):
	try:
		p = Web.objects.create(project_id=pid, shortname=shortname, url=url)
		p.save()
		return True

	except Exception as e:
		logger.error('Error adding web to database. {}'.format(e))
		return False

def updateWeb(shortname, url, pid, wid):
	try:
		if len(shortname) > 0:
			p = Web.objects.filter(id=wid).update(shortname=shortname)
		elif len(url) > 0:
			p = Web.objects.filter(id=wid).update(url=url)

		return True

	except Exception as e:
		logger.error('Error updating web on database. {}'.format(e))
		return False

# deletes a web
def deleteWeb(wid):
	try:
		Web.objects.filter(id=wid).delete()

		return True

	except Exception as e:
		logger.error('Error deleting web from database. {}'.format(e))
		return False

def updateWebStatus(pid, wid, fuzzer_name, status):
	try:
		p = Web.objects.filter(id=wid).update(last_fuzzer=fuzzer_name, fuzzer_status=status)
		return True

	except Exception as e:
		logger.error('Error updating web status on database. {}'.format(e))
		return False


def getWebInfo(wid):
	try:
		w = Web.objects.get(id=wid)

		return w

	except Exception as e:
		logger.error('Error retrieving information from web ID. {}'.format(e))
		return False

##############################
# Findings
##############################

def addFinding(wid, result):
	try:
		p = Finding.objects.create(web_id=wid, url=result.url, path=result.path, code=result.code, size=result.size)
		p.save()
		return True

	except Exception as e:
		logger.error('Error adding finding to database. {}'.format(e))
		return False

def updateFinding(wid, fid, path, url, code):
	try:
		p = Finding(web_id=wid, id=fid, path=path, url=url, code=code)
		p.save()

		return True

	except Exception as e:
		logger.error('Error updating finding on database. {}'.format(e))
		return False

def addManualFinding(wid, path, url, code):
	try:
		p = Finding.objects.create(web_id=wid, url=url, path=path, code=code)
		p.save()
		return True

	except Exception as e:
		logger.error('Error adding finding to database. {}'.format(e))
		return False

# deletes a finding
def deleteFinding(finding_id):
	try:
		Finding.objects.filter(id=finding_id).delete()
		logger.warning('Finding with id {} was deleted.'.format(finding_id))

		return True

	except Exception as e:
		logger.error('Error deleting finding from database. {}'.format(e))
		return False

def deleteAllFinding(wid):
	try:
		Finding.objects.filter(web_id=wid).delete()

		return True

	except Exception as e:
		logger.error('Error deleting all findings from database. {}'.format(e))
		return False

def getFindings(wid):
	try:
		findings = Finding.objects.filter(web_id=wid)
		return findings

	except Exception as e:
		logger.error('Error retrieving findings from database. {}'.format(e))
		return []

def getSingleFinding(fid):
	try:
		return Finding.objects.get(id=fid) 

	except Exception as e:
		logger.error('Error retrieving finding from database. {}'.format(e))
		return []



def getPagedFindings(wid, draw, order_col, order_dir, start, length, search_term):
	try:
		if order_dir == "desc":
			order_col = '-' + order_col #Order desc
		findings = Finding.objects.filter(web_id=wid).order_by(order_col)
		paginator = Paginator(findings, length)
		page = floor((start + 1) / length) + 1 # Pages start on 1

		object_list = paginator.page(page).object_list

		num_rows = len(findings)

		data = [
			[
				finding.path,
				'''<a href="{}">{}</a>'''.format(finding.url, finding.url),
				finding.size,
				finding.code,
				'''<button type="button" class="btn btn-primary" onclick="editFindingModal({});"><i class="fas fa-edit"></i> Edit</button>
				   <button type="button" class="btn btn-primary" onclick="deleteFinding({})"><i class="fas fa-trash"></i> Delete</button>'''.format(finding.id, finding.id)
			] for finding in object_list
		]

		return json.dumps({
			'draw': draw,
			'recordsTotal': num_rows,
			'recordsFiltered': num_rows,
			'data': data
		})

	except Exception as e:
		logger.error('Error retrieving paged findings from database. {}'.format(e))
		return json.dumps({
			'draw': draw,
			'recordsTotal': 0,
			'recordsFiltered': 0,
			'data': [],
			'error': "Error retrieving paged findings from database."
		})	