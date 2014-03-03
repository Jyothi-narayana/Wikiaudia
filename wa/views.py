# -*- coding: utf-8 -*-
from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
import json
from django.core import serializers
from django.conf import settings
import os
from PIL import Image
from django.core.urlresolvers import reverse
from wa.models import Language,Book, Paragraph, UserHistory, Document, CustomUser# Create your views here.
from wa.forms import DocumentForm
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from django.contrib.auth.forms import UserCreationForm
from forms import CustomUserCreationForm
from django.shortcuts import render
from fpdf import FPDF
from wa.tasks import soundProcessingWithAuphonicTask,uploadSplitBookIntoGridFS
from django.core.urlresolvers import reverse
import logging
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from wa.paragraphChunks import getChunkID
from wa.dbOps import uploadDigiDb, uploadAudioDb
#from wa.splitBook import splitBookIntoPages
# Create your views here.

def error_processor(request):
    if 'error' in request.session:
        return {'msg': request.session['error']}
    else:
        return {}
    
def front(request):
    if request.user.is_authenticated():
        response=HttpResponseRedirect('/wa/home')
    else:
        c=RequestContext(request,{'foo':'bar',},[error_processor])
        if 'error' in request.session:
            del request.session['error']
        response=render_to_response('wa/session/front.html',c)
    return response
    
def logout(request):
    auth.logout(request)
    #return render_to_response('WikiApp/session/front.html')    
    return HttpResponseRedirect('/wa')
    
def auth_view(request):
    username= request.POST.get('username','')
    password= request.POST.get('password','')
    user= auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/wa/home')
    else:
        request.session['error'] = "Username and Password do not match.Try Again!"
        return HttpResponseRedirect('/wa')
#Have not done auth.logout(request) 
def home(request):
    if request.user.is_authenticated():
        return render_to_response('wa/session/home.html', {'full_name':request.user.first_name,'languages_known':request.user.languages_known,'points':request.user.points })
    #return render_to_response('WikiApp/session/home.html', {'full_name':request.user.userprofile.Languages})
    else:
        return HttpResponseRedirect('/wa')

def register_user(request):
    if request.method == 'POST':
        form=CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            #languages_known_v = form.Languages
            log = logging.getLogger("wa")
            #log.info(languages_known_v)
            return HttpResponseRedirect('/wa/register_success')
    else:
        form= CustomUserCreationForm()
    return render(request,  'wa/session/register.html', {
        'form': form,
    })

def register_success(request):
    return render_to_response('wa/session/register_success.html')

def digiSelection(request):
    if request.user.is_authenticated():
        #return render_to_response('wa/AudioDigi/Digitize.html')
        request.session['action'] = "digitize";
        #langs = Language.objects.all()
	user_id = request.user.id
	user_langs = CustomUser.objects.get(pk = user_id).languages_known.split(',')
        context = RequestContext(request, {'langs': user_langs, } )
        return render(request, 'wa/chooseLanguage.html', context)
    else :
        return HttpResponseRedirect('/wa')

def audioSelection(request):
    if request.user.is_authenticated():
        log = logging.getLogger("wa")
        log.info("in audio Selection")
        #languages = Language.objects.all()
        #context = {'all_languages' : all_languages}
        #return render(request, 'wa/audio.html', context)
        #return HttpResponse("You're looking at the results of poll ")
        request.session['action'] = "record";
        #langs = Language.objects.all()
        #context = {'langs': langs}
	user_id = request.user.id
	user_langs = CustomUser.objects.get(pk = user_id).languages_known.split(',')
        context = RequestContext(request, {'langs': user_langs, } )
        return render(request, 'wa/chooseLanguage.html', context)
    else :
        return HttpResponseRedirect('/wa')

def getImage(request, book_id):
    response = HttpResponse(mimetype = "image/jpg")
    path_to_save = str(book_id) +"/bookThumbnail.png"
    a = default_storage.open(path_to_save)
    local_fs = FileSystemStorage(location='/tmp/pdf')
    local_fs.save(a.name,a)
    image = Image.open("/tmp/pdf/"+a.name)
    image.save(response, 'png')
    local_fs.delete(a.name)
    return response

def digitize(request, book_id):
    if request.user.is_authenticated():
        print("user_id:" + str(request.user.id))
        para_id = getChunkID(request.user.id,book_id,0)
        print("para_id: " + str(para_id))
        return render_to_response('wa/AudioDigi/Digitize.html', {'book_id': book_id, 'para_id': para_id} )
    else :
        return render_to_response('wa/AudioDigi/Digitize.html')

def audioUpload(request, book_id):
    if request.user.is_authenticated():
        # Handle file upload
        '''
        Add additional inputs to post to figure out the book and 
        the paragraph number so that the upload takes place in that folder
        Current working : Saves the file with a fixed name and the file sent for API processing is fixed as well. 
        Both of these should be made dynamic 
        '''
        if request.method == 'POST':
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                newdoc = Document(docfile = request.FILES['docfile'])
                newdoc.docfile.save('Ashu.wav',request.FILES['docfile'])
                #soundProcessWithAuphonic('documents/Ashu.wav')
                #soundProcessingWithAuphonicTask.delay('../documents/ashu.mp3')
                return HttpResponseRedirect(reverse('wa.views.audioSelection'))
        else:
            form = DocumentForm() # A empty, unbound form

        # Load documents for the list page
        documents = Document.objects.all()
        para_id = getChunkID(request.user.id, book_id, 0)
        # Render list page with the documents and the form
        return render_to_response(
            'wa/audioUpload.html',
            {'documents': documents, 'form': form, 'book_id': book_id, 'para_id': para_id },
           
            context_instance=RequestContext(request)
        )
    else :
        return render_to_response('/wa')

def chooseAction(request, book_id):
    if(request.session['action'] == "digitize"):
        resp = digitize(request, book_id)
    elif(request.session['action'] == "record"):
        resp = audioUpload(request, book_id)
    return resp;

def getParagraph(request, book_id, para_id): 
    #Should be served by nginx-gridfs
    response = HttpResponse(mimetype = "image/jpg")
    '''
    image = Image.open(os.path.dirname(settings.BASE_DIR) + "/" + "wastore/hindi.jpg") 
    image.save(response, 'png')
    #image = Image.open(settings.BASE_DIR) 
    '''
    path_to_save = str(book_id) + "/chunks/" + str(para_id) + "/image.png"
    a = default_storage.open(path_to_save)
    local_fs = FileSystemStorage(location='/tmp/pdf')
    local_fs.save(a.name,a)
    image = Image.open("/tmp/pdf/"+a.name)
    image.save(response, 'png')
    local_fs.delete(a.name)
    return response

'''
upload the recorded audio file to the server 
'''
def audioUploadForm(request, book_id, para_id):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            #newdoc.save()
            
            #The Above call is just temoraray 
            #Use this if the name of the file is to be changed and saved with a path
            file_name = str(book_id)+"_"+str(para_id)+"_"+"sound.wav"
            newdoc.docfile.save(file_name,request.FILES['docfile'])
            #soundProcessWithAuphonic('documents/Ashu.wav')
            user_id = request.user.id
            soundProcessingWithAuphonicTask.delay('documents/'+file_name,book_id,para_id,user_id)
    return HttpResponseRedirect(reverse('wa.views.audioSelection')) 
        
                
def chooseAction(request, book_id):
    if(request.session['action'] == "digitize"):
        resp = digitize(request, book_id)
    elif(request.session['action'] == "record"):
        resp = audioUpload(request, book_id)
    return resp;

def langBooks(request):
    #print(os.path.dirname(settings.BASE_DIR))
    #outside = os.path.dirname(settings.BASE_DIR)
    #if(os.path.exists())
    language = request.GET['language']
    #print(language);
    language = Language.objects.get(langName = language)
    #print(language)
    languageBooks = language.book_set.all()
    ret = serializers.serialize("json", languageBooks)
    #resp = HttpResponse(content_type = "application/json");
    #json.dump(languageBooks, resp)
    return HttpResponse(ret)


#def audioUpload(request):
    
    
def uploadBook(request):
    # Handle file upload
    if request.user.is_authenticated():
        if request.method == 'POST':

            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                log = logging.getLogger("wa")
                log.info("Upload Book :")
                log.info(request.POST['language'])
                b = Book(lang = Language.objects.get(langName = request.POST.get("language", "")), author = request.POST.get("author", ""), bookName = request.POST.get("bookName", ""))
                b.save()
                
                
                newdoc = Document(docfile = request.FILES['docfile'])

                #newdoc.docfile.save(str(b.id) + "/original/originalBook.pdf", request.FILES['docfile'], save=False)
                newdoc.docfile.save(str(b.id), request.FILES['docfile'], save=False)
                a = default_storage.open("documents/"+str(b.id))
                local_fs = FileSystemStorage(location='/tmp/pdf')
                local_fs.save(a.name,a)
                #b = default_storage.save(str(b.id) + "/original/originalBook.pdf",a)
                
                log.info((a.name))
                mod_path = "/tmp/pdf/"+a.name
                f = open(mod_path, 'r')
                myfile = File(f)
                new_name =str(b.id) + "/original/originalBook.pdf"
                default_storage.save(new_name,myfile)
                os.remove(mod_path)
                #--TODO--add it to user history
                #splitBookIntoPages(str(b.id) + "/original/originalBook.pdf")
                uploadSplitBookIntoGridFS.delay( str(b.id) + "/original/originalBook.pdf", b.id)
                # Redirect to the document list after POST
                #delete the file from default storage
                default_storage.delete("documents/"+ str(b.id))
                return HttpResponseRedirect(reverse('wa.views.audioSelection'))
        else:
            form = DocumentForm() # A empty, unbound form
            #langs = Languages.objects.all()
        # Render list page with the documents and the form
	    langs = Language.objects.all()
        return render_to_response(
            'wa/uploadBook.html',

            {'form': form,'langs':Language.objects.all()},
            context_instance=RequestContext(request)
        )
    else :
        return render_to_response('/wa')

def uploadDigi(request, book_id, para_id):
    if request.POST.has_key('unicode_data'):
        file = open("DigiFiles/KannadaInput.txt", "w")
        file.write((request.POST['unicode_data']).encode('utf8'))
        file.close()
        f = open("DigiFiles/KannadaInput.txt", "r")
    #get latest version and then save
        path_to_save = str(book_id) + "/chunks/" + str(para_id) + "/DigiFiles/1.txt"
        default_storage.save(path_to_save, File(f))
        f.close()  
	#delete file - todo
        #concatenateDigi(request)
        #pdfGen(request)
        user_id = request.user.id
        uploadDigiDb(para_id, user_id)
        x = request.POST['unicode_data']
        return HttpResponse(x)
    
def ajax(request):
    if request.POST.has_key('client_response'):
        x = request.POST['client_response']                 
        #y = socket.gethostbyname(x)                          
        response_dict = {}                                         
        #response_dict.update({'server_response': y })                                                                  
        return HttpResponse('Success')
    else:
        return render_to_response('WikiApp/AudioDigi/trial.html', context_instance=RequestContext(request))     
        
def concatenateDigi(request):
    filenames = ['DigiFiles/one.txt','DigiFiles/two.txt']
    with open('DigiFiles/final.txt', 'w') as fout:
        for line in fileinput.input(filenames):
            fout.write(line)
def pdfGen(request):
    pdf = FPDF()
    pdf.add_page()
    #pdf.add_font('gargi', '', 'gargi.ttf', uni=True) 
    #pdf.set_font('gargi', '', 14)
    #pdf.write(8, u'Hindi: एक अमरीकि')
    pdf.add_font('Kedage-b', '', 'Kedage-b.ttf', uni=True) 
    pdf.set_font('Kedage-b', '', 14)
    #pdf.add_font('TSCu_SaiIndira', '', 'TSCu_SaiIndira.ttf', uni=True) 
    #pdf.set_font('TSCu_SaiIndira', '', 14)
    linestring = open('DigiFiles/KannadaInput.txt', 'r').read()
    pdf.write(8,linestring)
    pdf.ln(20)
    pdf.output("DigiFiles/KannadaOutput.pdf", 'F')
            
            

    
