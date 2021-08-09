import wfuzz
import multiprocessing
import logging
from app.backend import database
from django import db

logger = logging.getLogger(__name__)


running_processes = []

def getRunningJobs():
	return len(running_processes)

class Result:
	def __init__(self, wid, url, path, size, code):
		self.wid = wid
		self.url = url
		self.path = path
		self.size = size
		self.code = code
		self.redirection = ""

def webFuzz(wid, web, fuzzer):
	try:

		payload = "-Z -t {} ".format(fuzzer.threads)

		if fuzzer.hide_codes and len(fuzzer.hide_codes) > 1:
			payload += "--hc {} ".format(fuzzer.hide_codes)


		if fuzzer.proxy and len(fuzzer.user_agent) > 1:
			payload += "-p {} ".format(fuzzer.proxy)

		if fuzzer.extensions and len(fuzzer.extensions) > 1:
			extensions = fuzzer.extensions.replace(',','-')
			extensions += '-' # Empty extension

			payload += "-w {} -z list,{} {}/FUZZFUZ2Z".format(fuzzer.wordlist, extensions, web)

		else:
			payload += "-w {} {}/FUZZ".format(fuzzer.wordlist, web)

		logger.warning("Fuzz payload: wfuzz.py {}".format(payload))
		s = wfuzz.get_session(payload)

		if fuzzer.user_agent and len(fuzzer.user_agent) > 1:
			payload += '-H "User-Agent: {}" '.format(fuzzer.user_agent)

		
			res = list(s.fuzz(headers=[("User-Agent", fuzzer.user_agent),]))

		else:
			res = list(s.fuzz())



		results = []
		for r in res:
			results.append(Result(wid, r.url, r.description.replace(' - ', ''), r.chars, r.code))

		return results

	except Exception as e:
		logger.error('Error while fuzzing. Exception: {}'.format(e))
		return None



def daemon(pid, web, fuzzer):
	logger.warning('Fuzzing on {} started.'.format(web.web))

	results = webFuzz(web.wid, web.web, fuzzer)

	if results is None:
		database.updateWebStatus(pid, web.wid, fuzzer.name, "ERROR")
		logger.error('Fuzzing on {} finished with errors.'.format(web.web))
		killJob(web, pid)
		return


	for r in results:
		database.addFinding(web.wid, r)

	logger.warning('Fuzzing on {} finished.'.format(web.web))
	database.updateWebStatus(pid, web.wid, fuzzer.name, "FINISHED")
	killJob(web, pid)


def checkStatus(pid):
	try:
		# Get webs with RUNNING status
		webs = database.getRunningWebs(pid)

		for web in webs:

			alive = False
			process = None

			for p in running_processes:

				# Process has finished but still lives in the array
				if not p.is_alive():
					running_processes.remove(p)
					continue

				# Process has not finished and still lives in the array
				if p.name == web.url:
					alive = True
					process = p

			# There is no process in the array which the same name as current web
			if not alive:
				database.updateWebStatus(pid, web.id, web.last_fuzzer, "KILLED")


	except Exception as e:
		logger.error('Error checking status (fuzzer). {}'.format(e))
		return False


def killJob(web, pid):
	try:

		for p in running_processes:

			if p.name == web.url:
				p.terminate()
				running_processes.remove(p)

				database.updateWebStatus(pid, web.id, web.last_fuzzer, "KILLED")
				return True

		return False

	except Exception as e:
		logger.error('Error killing job (fuzzer). {}'.format(e))
		return False



def launch(pid, web, fuzzer):

	try:

		# Web is already being fuzzed
		for p in running_processes:
			if p.name == web.web:
				return -1

		# Updates status to RUNNING
		database.updateWebStatus(pid, web.wid, fuzzer.name, "RUNNING")

		db.connections.close_all()

		# Creates thread
		d = multiprocessing.Process(
			name=web.web,
			target=daemon,
			args=(pid, web, fuzzer)
		)

		# Daemon
		d.daemon = True


		# Appends to running_processes
		running_processes.append(d)
		
		d.start()

		return True

	except Exception as e:
		logger.error('Launch error in fuzz.py. {}'.format(e))
		return False
