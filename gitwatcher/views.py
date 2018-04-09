from django.shortcuts import render
from django.http import HttpResponse
import os
import zipfile
from gitinspector import gitinspector as git
import boto3
import botocore
from django.template import RequestContext, loader
# Create your views here.

def index(request):
	return render(request,'gitwatcher/index.html')

def clonegit(request):
	return render(request,'gitwatcher/clonegit.html')

def gitwatch1(request, address):
	address = 'https://github.com/' + address
	os.chdir('/home/ubuntu')
	os.system('git clone ' + address + '.git')
	words = address.split('/')
	length = len(words)
	os.chdir('/home/ubuntu/' + words[length-1])
	os.system('python3 /home/ubuntu/gitinspector/gitinspector.py -F html > /home/ubuntu/ttests/gitwatcher/templates/gitwatcher/statistics1.html')
	#git.main(words[length-1])
	os.chdir('/home/ubuntu')
	os.system('rm -rf ' + words[length-1])

	#html_output = 'gitwatcher/' + words[length-1] + '.html'
	return render(request, 'gitwatcher/statistics1.html')

def storedData(request):
	path = '/home/ubuntu/html'
	files = os.listdir(path)
	context = {}

	for i in range(0,len(files)):
		temp = files[i].split('_')
		cap_key_temp = temp[1].split('-')
		cap_key = cap_key_temp[0] + '_' + cap_key_temp[1] + '_' + cap_key_temp[2]
		if cap_key in context:
			branch = temp[3]
			for j in range(4,len(temp)):
				branch += '_'
				branch += temp[j]
			context[cap_key].append(branch)
		else:
			context[cap_key] = []
			branch = temp[3]
			for j in range(4,len(temp)):
				branch += '_'
				branch += temp[j]
			context[cap_key].append(branch)


	return render(request,'gitwatcher/storedData.html',context)

def gitwatch2(request, address, branch):
	address_words = address.split('/')
	branch_words = branch.split('/')
	branch_len = len(branch_words)

	branch_KEY_address = branch_words[0]
	for i in range(1, branch_len):
		branch_KEY_address += '_' + branch_words[i]

	BUCKET_NAME = 'gittos3fixed-outputbucket-ix0jgogj97ai'
	KEY = address + '/branch/' + branch + '/' + address_words[0] + '_' + address_words[1] + '_branch_' + branch_KEY_address + '.zip'
	s3 = boto3.resource('s3')
	try:
		s3.Bucket(BUCKET_NAME).download_file(KEY, '/home/ubuntu/git_repo.zip')
	except botocore.exceptions.Clienterror as e:
		if e.response['Error']['Code'] == '404':
			print("The object does not exist.")
		else:
			raise

	os.chdir('/home/ubuntu')
	os.system('unzip git_repo.zip -d ./git_repo')
	os.chdir('/home/ubuntu/git_repo')
	git.main(address_words[1])
	os.chdir('/home/ubuntu')
	os.system('rm -rf git_repo.zip')
	os.system('rm -rf git_repo')
	#os.system('python3 /home/ubuntu/gitinspector/gitinspector.py -F html > /home/ubuntu/ttests/gitwatcher/templates/gitwatcher/statistics2.html')

	html_output = 'gitwatcher/' + address_words[1] + '.html'
	return render(request, html_output)