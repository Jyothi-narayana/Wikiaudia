from celery import Celery
import sys
import getpass
import time
import requests
from splitBook import splitBookIntoPages
from requests.auth import HTTPBasicAuth
from wa.models import Language, Book, Paragraph, UserHistory, Document
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.core.files.base import ContentFile
from wand.image import Image
from wa.dbOps import uploadAudioDb
#from wa.dbOps import addParagraph
#from wa.models import Language,Book, Paragraph, UserHistory, Document
#import wikiaudia.settings
import re,os,sys
import logging

API_URL = "https://auphonic.com/api/simple/productions.json"
API_DETAILS_URL = "https://auphonic.com/api/production/%s.json"

app = Celery('tasks', broker='redis://localhost')

#@app.task
#def add(x, y):
#    return x + y
@app.task(name='wa.tasks.soundProcessingWithAuphonicTask')
def soundProcessingWithAuphonicTask(f,book_id,para_id,user_id):
	username = 'ashuven63@gmail.com'
	password = 'ashu177'
	preset = 'aPZCk3SVNZGPUfPGEgA76Q'
	a = default_storage.open(f)
	local_fs = FileSystemStorage(location='/tmp/audiofiles')
	local_fs.save(a.name,a)
	data = {'preset': preset, 'action': 'start', }
	input_files = {}
	input_files['input_file'] = open('/tmp/audiofiles/'+f, 'r')
	print "opened file"
	response_upload = requests.post(API_URL, data=data, files=input_files,auth=HTTPBasicAuth(str(username), str(password)))
	json_response = response_upload.json()
	uuid = json_response['data']['uuid']
	detail_url = API_DETAILS_URL % uuid
	headers = {'content-type': 'application/json'}
	getDetails = True
	noOfTries = 0
	while getDetails and noOfTries<5:
		detail_response_upload = requests.get(detail_url,headers=headers,auth=HTTPBasicAuth(str(username), str(password)))
		detail_object = detail_response_upload.json()
		print detail_object['data']['status_string']
		if detail_object['data']['status_string']=='Done':
			getDetails=False
			continue
		time.sleep(10)
		noOfTries=noOfTries+1
	download_url = detail_object['data']['output_files'][0]['download_url']
	#use this URL to download back into the server 
	out = requests.get(download_url,auth=HTTPBasicAuth(str(username), str(password)))
	#trialFile = open('trial.mp3','w')
	#trialFile.write(out.content)
	trialFile = ContentFile(out.content)
	#Warning : hardcoded value
	default_storage.save(str(book_id) + "/chunks/" + str(para_id) + "/AudioFiles/1.wav",trialFile)
	uploadAudioDb(para_id, user_id)
	default_storage.delete(f)
	#trialFile.close()


	print download_url		
	return 0

@app.task(name='wa.tasks.uploadSplitBookIntoGridFS')
def uploadSplitBookIntoGridFS(f,bookID):
	splitBookIntoPages(f,bookID)