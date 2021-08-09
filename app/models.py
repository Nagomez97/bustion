from django.db import models

# Create your models here.

class Project(models.Model):
	name = models.CharField(max_length=50)
	date = models.DateTimeField(auto_now=True)

class Fuzzer(models.Model):
	name = models.CharField(max_length=100)
	threads = models.IntegerField()
	wordlist = models.CharField(max_length=100)
	user_agent = models.CharField(max_length=100)
	extensions = models.CharField(max_length=100)
	hide_codes = models.CharField(max_length=100)
	verb = models.CharField(max_length=10)
	proxy = models.CharField(max_length=100, default="")
	project = models.ForeignKey(Project, on_delete=models.CASCADE)



class Web(models.Model):
	url = models.CharField(max_length=100)
	shortname = models.CharField(max_length=100)
	project = models.ForeignKey(Project, on_delete=models.CASCADE)
	fuzzer_status = models.CharField(max_length=100, default="")
	last_fuzzer = models.CharField(max_length=100, default="")

class Finding(models.Model):
	path = models.CharField(max_length=100)
	url = models.CharField(max_length=100, default='')
	size = models.CharField(max_length=100, default="0")
	code = models.CharField(max_length=100, default="-")
	web = models.ForeignKey(Web, on_delete=models.CASCADE)
	

