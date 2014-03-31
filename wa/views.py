# -*- coding: utf-8 -*-
from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
import json
from django.core import serializers
from django.utils import simplejson
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
from django.db.models import F
import wave
import BeautifulSoup
from validate_email import validate_email
from utilities import pointsToAward

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
        #ret = myprofile(request)
        #return ret
    #return render_to_response('WikiApp/session/home.html', {'full_name':request.user.userprofile.Languages})
    else:
        return HttpResponseRedirect('/wa')

def aboutUs(request):
	return render_to_response('wa/aboutUs.html')

def aboutUsOut(request):
	return render_to_response('wa/aboutUsOut.html')

'''	
def contributeOut(request):
	return render_to_response('wa/contributeOut.html')
'''
	
def register_user(request):
    emailValue="" 	
    nameValue=""
    phNo=""	
    if request.method == 'POST':
        form=CustomUserCreationForm(request.POST)
        print("printing from register_user")	
        formStr=str(form)	
        #print(formStr)		
        	
        soup = BeautifulSoup.BeautifulSoup(formStr)
        val=soup.find(id="id_email")
        print(val['value'])	
        emailValue=val['value']	
        try:		
            is_valid = validate_email(val['value'],verify=True)
        except Exception, e:
            is_valid=False		
        val=soup.find(id="id_phoneNo")
        phNo=val['value']
        val=soup.find(id="id_first_name")
        nameValue=val['value']		
        print("is_valid")
        print(is_valid)				
        #print(form.Meta.model.USERNAME_FIELD)		
        #print(formStr)		
        	
        if (form.is_valid() & is_valid):
            form.save()
            #languages_known_v = form.Languages
            log = logging.getLogger("wa")
            #log.info(languages_known_v)
            return HttpResponseRedirect('/wa/register_success')
        else:
            form=CustomUserCreationForm(request.POST)
            #print(form.id_email)			
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

def myprofile(request):
    if request.user.is_authenticated():
        user_id = request.user.id
        points = CustomUser.objects.get(pk = user_id).points
        userActions = UserHistory.objects.filter(user = CustomUser.objects.get(pk = user_id))
        digi = userActions.filter(action = 'di')
        rec = userActions.filter(action = 're')
        upl = userActions.filter(action = 'up')
        digiN = digi.count()
        recN = rec.count()
        uplN = upl.count()
        context = RequestContext(request, {'digiNum': digiN,'recNum' : recN, 'uploadNum' : uplN, 'points' : points} )
        return render(request, 'wa/myprofile.html', context)
    else:
        return HttpResponseRedirect('/wa')

def userDetailsLangwise(request):
    category = request.GET['category']
    log = logging.getLogger("wa")
    log.info("category " + category)
    user_id = request.user.id
    userActions = UserHistory.objects.filter(user = CustomUser.objects.get(pk = user_id))
    ofCategory = userActions.filter(action = category)
    log.info("count: %d", ofCategory.count())
    res = []
    if(category == "up"):
        print("coming to up")
        langs = Language.objects.all()
        for l in langs:
            print(l)
            c = ofCategory.filter(uploadedBook__lang__langName = l).count()
            if(c > 0):
                temp = {}
                temp['language'] = l.langName
                temp['count'] = c
                res.append(temp)
    else:
        user_langs = CustomUser.objects.get(pk = user_id).languages_known.split(',')
        for l in user_langs:
            log.info(l)
            l = l.strip()
            '''
            if(category == "up"):
                c = ofCategory.filter(uploadedBook__lang__langName = l).count()
            else:
            '''
            c = ofCategory.filter(paragraph__book__lang__langName = l).count()
            log.info(c)
            if(c > 0):
                temp = {}
                temp['language'] = l
                temp['count'] = c
                res.append(temp)
    log.info(res)
    #res = serializers.serialize("json", res)
    return HttpResponse(simplejson.dumps(res), content_type = "application/javascript; charset=utf8")
    #return HttpResponse(simplejson.dumps(res))

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
        para_id = getChunkID(request.user.id,book_id,1)
        print("para_id: " + str(para_id))
        if(para_id != 0):
            #request.session['language']='abc'        		
            return render(request,'wa/AudioDigi/Digitize.html', {'book_id': book_id, 'para_id': para_id} )
        else:
            return render_to_response('wa/error.html')
    else :
        return HttpResponseRedirect('/wa')

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
                log = logging.getLogger("wa")
                log.info(request.POST['yes'])
                #soundProcessWithAuphonic('documents/Ashu.wav')
                #soundProcessingWithAuphonicTask.delay('../documents/ashu.mp3')
                return HttpResponseRedirect(reverse('wa.views.audioSelection'))
        else:
            form = DocumentForm() # A empty, unbound form

        # Load documents for the list page
        documents = Document.objects.all()
        para_id = getChunkID(request.user.id, book_id, 0)
        # Render list page with the documents and the form
        if(para_id != 0):
            return render_to_response(
                'wa/audioUpload.html',
                {'documents': documents, 'form': form, 'book_id': book_id, 'para_id': para_id },
                context_instance=RequestContext(request)
            )
        else:
            return render_to_response('wa/error.html')
    else :
        return render_to_response('/wa')
def getAudio(request, book_id, para_id): 
    #Should be served by nginx-gridfs
    #response = HttpResponse(mimetype = "audio/x-wav")
    '''
    image = Image.open(os.path.dirname(settings.BASE_DIR) + "/" + "wastore/hindi.jpg") 
    image.save(response, 'png')
    image = Image.open(settings.BASE_DIR) 
    '''
    #response=HttpResponse()	
    path_to_save = "documents/"+str(book_id) + "_" + str(para_id) + "_sound.wav"
    #path_to_save = str(book_id) + "/chunks/" + str(para_id) + "/AudioFiles/1.wav"
    print(path_to_save)
    a = default_storage.open(path_to_save)
    local_fs = FileSystemStorage(location='/tmp/audio')
    local_fs.save(a.name,a)
    file = open("/tmp/audio/documents/"+str(book_id) + "_" + str(para_id) + "_sound.wav", "rb").read() 
    #response['Content-Disposition'] = 'attachment; filename=filename.mp3' 
    

    #audio = wave.open("/tmp/audio/"+a.name,'r')
    #--audio.save(response, 'wav')
    #data=audio.readframes(audio.getnframes())	
    #print len(data)
    #print type(data)
    #print data[9000:9002]	
    #--response.write(data)
    #response = HttpResponse(content=data, mimetype="audio/x-wav")
    #print response.content[9000:9002]	
    #audio.close()
    
    local_fs.delete(a.name)
    
    #return HttpResponse("hello")
    return HttpResponse(file, mimetype="audio/wav") 
def upVoted(request, book_id, para_id):
	paraToUpVote=Paragraph.objects.get(pk=para_id)
	print paraToUpVote
	#paraToUpVote.update(upVotes=1)
	#paraToUpVote.upVotes=paraToUpVote.upVotes+1
	paraToUpVote.upVotes = F('upVotes') + 1
	paraToUpVote.save()
	return HttpResponseRedirect('/wa')
	
def downVoted(request, book_id, para_id):
	paraToDownVote=Paragraph.objects.get(pk=para_id)
	#paraToUpVote.update()
	paraToDownVote.downVotes = F('downVotes') + 1
	paraToDownVote.save()
	return HttpResponseRedirect('/wa')
	
def bookParas(request):
    print("Into bookParas")
    #print(os.path.dirname(settings.BASE_DIR))
    #outside = os.path.dirname(settings.BASE_DIR)
    #if(os.path.exists())
    
    book = request.GET['book_id']
    print("book")
    print book
    #print(language);
    bookTemp=book
    book = Book.objects.get(id = book)
    print(book)
    #print(language)
    
    
    #bookParagraphs = book.paragraph_set.all()[:10]
    bookParagraphs = Paragraph.objects.filter(book__id=bookTemp).filter(status='va')[:5]
	
    #bookParagraphs = book.paragraph_set.filter(status_id='re')[:4]
    #bookParagraphs = book.paragraph_set.all.filter(status='re')[:5]
	
	#print(bookParagraphs)
    
    ret = serializers.serialize("json", bookParagraphs)
    
	
	#resp = HttpResponse(content_type = "application/json");
    #json.dump(languageBooks, resp)
    
    #return HttpResponse(ret)
	
    return HttpResponse(ret)
def validatePool(request,book_id):
	if request.user.is_authenticated():
		return render_to_response('wa/validatePool.html', {'book_id': book_id})
	else :
		return render_to_response('/wa')
		
def validatePara(request,book_id,para_id):
	if request.user.is_authenticated():
		return render_to_response('wa/validate.html', {'book_id': book_id,'para_id': para_id})
	else :
		return render_to_response('/wa')
		
def getParaImage(request,book_id,para_id):
    response = HttpResponse(mimetype = "image/jpg");
    path = os.path.dirname(settings.BASE_DIR) + "/" + "wastore/" + book_id + "/" + "frontcover.jpg"
    #print(path);
    if(os.path.exists(path)):
       image = Image.open(path)
    else:
       image = Image.open(os.path.dirname(settings.BASE_DIR) + "/" + "wastore/" + "default/" + "frontcover.jpg")
    image.save(response, 'png');
    return response; 
def chooseParaAction(request, book_id,para_id):
	if(request.session['action'] == "digitize"):
		resp = digitize(request, book_id)
	elif(request.session['action'] == "record"):
		resp = audioUpload(request, book_id)
	elif(request.session['action'] == "validate"):
		resp = validatePara(request, book_id,para_id)
	return resp;

def valSelection(request):
	if request.user.is_authenticated():
		#return render_to_response('wa/AudioDigi/Digitize.html')
		request.session['action'] = "validate";
        	user_id = request.user.id
        	user_langs = CustomUser.objects.get(pk = user_id).languages_known.split(',')
		context = RequestContext(request, {'langs': user_langs, } )
		return render(request, 'wa/chooseLanguage.html', context)
	else :
		return HttpResponseRedirect('/wa')
		
def chooseAction(request, book_id):
    if(request.session['action'] == "digitize"):
        resp = digitize(request, book_id)
    elif(request.session['action'] == "record"):
        resp = audioUpload(request, book_id)
    elif(request.session['action'] == "validate"):
        resp = validatePool(request, book_id)
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
            log = logging.getLogger("wa")
            log.info(request.POST['chapterrad'])
            isChapter = request.POST['chapterrad']
            para = Paragraph.objects.get(pk = para_id)
            if isChapter=='yes':
                para.isChapter = True
            else:
                para.isChapter = False
            para.save()
            #soundProcessWithAuphonic('documents/Ashu.wav')
            user_id = request.user.id
            #set it before sending it for processing to avoid showing it again for recording But change appropriately if an error occurs while processing
            uploadAudioDb(para_id, user_id)
            soundProcessingWithAuphonicTask.delay('documents/'+file_name,book_id,para_id,user_id)
    return HttpResponseRedirect(reverse('wa.views.audioSelection')) 
        

def langBooks(request):
    #returns a JSON object with all books of a language which haven't been completed depending on the action
    
    language = request.GET['language']
    language = language.strip()
    request.session['language']=language
    print(language)
    language = Language.objects.get(langName = language)
    #Only send those books which aren't finished yet
    #languageBooks = language.book_set.all()
    languageBooks = Book.objects.filter(lang = language)
    if(request.session['action'] == "digitize"):
        languageBooks = languageBooks.exclude(percentageCompleteDigi = F('numberOfChunks'))
    elif(request.session['action'] == "record"):
        languageBooks = languageBooks.exclude(percentageCompleteAudio = F('numberOfChunks'))
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
                b = Book(lang = Language.objects.get(langName = request.POST.get("language", "")), author = request.POST.get("author", ""), bookName = request.POST.get("bookName", ""), shouldConcatAudio = True, shouldConcatDigi = True)
                b.save()
                user_id = request.user.id
                uh = UserHistory(user = CustomUser.objects.get(pk = user_id), action = 'up', uploadedBook = b)
                uh.save()
                # add points
                user = CustomUser.objects.get(pk = user_id)
                user.points = user.points + pointsToAward("up")
                user.save()
                
                newdoc = Document(docfile = request.FILES['docfile'])

                #newdoc.docfile.save(str(b.id) + "/original/originalBook.pdf", request.FILES['docfile'], save=False)
                newdoc.docfile.save(str(b.id), request.FILES['docfile'], save=False)
                a = default_storage.open("documents/"+str(b.id))
                local_fs = FileSystemStorage(location='/tmp/pdf')
                local_fs.save(a.name,a)
                #b = default_storage.save(str(b.id) + "/original/originalBook.pdf",a)
                #default_storage.close("documents/"+str(b.id))
                log.info((a.name))
                mod_path = "/tmp/pdf/"+a.name
                f = open(mod_path, 'rb')
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
    print("coming to upload digi")
    
    #TODOJO
    #IsChapter from digitization. Not able to execute this. If the value of isChapter
    #id retrieved properly go ahead and set it as the attribute of the paragraph
    if request.POST.has_key('isChapter'):
        isChapter = request.POST['isChapter']
        log = logging.getLogger("wa")
        log.info("Upload Digi:"+isChapter)
        para = Paragraph.objects.get(pk = para_id)
        #if(isChapter)
        #para.isChapter = isChapter
        if(isChapter == "true"):
            print("coming to true")
            para.isChapter = True
        elif(isChapter == "false"):
            print("coming to false")
            para.isChapter = False
        para.save()
        print("para.isChapter: " + str(para.isChapter))
    if request.POST.has_key('unicode_data'):
        file_name = "/tmp/Digi" + str(para_id) + ".txt"
        file = open(file_name, "w")
        file.write((request.POST['unicode_data']).encode('utf8'))
        file.close()
        f = open(file_name, "r")
        #get latest version and then save
        path_to_save = str(book_id) + "/chunks/" + str(para_id) + "/DigiFiles/1.txt"
        default_storage.save(path_to_save, File(f))
        f.close()  
	    #delete file - todo
        os.remove(file_name)
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

