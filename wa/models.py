#!/usr/bin/env python
# -*- coding: utf8 -*-
from fpdf import FPDF
import os
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.db import models
from django.utils import timezone
from separatedvaluesfield.models import SeparatedValuesField
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save#, post_save, pre_delete, post_delete, request_started, request_finished
from django.dispatch import receiver
import logging
from datetime import datetime
#import wave


# Create your models here.
# Have used camel case for all var names

fontLanguageMap = {'Assamese':'lohit_bn','Bengali':'MuktiNarrow','Bodo':'gargi','Dogri':'gargi','Gujarati':'lohit_gu','Hindi':'gargi',
'Kannada':'Kedage-b','Konkani':'gargi','Maithili':'gargi','Malayalam':'','Manipuri':'',
'Marathi':'gargi','Nepali':'gargi','Oriya':'','Punjabi':'','Sanskrit':'gargi',
'Santali':'gargi','Sindhi':'gargi','Tamil':'TSCu_SaiIndira','Telugu':'','English':'Sawasdee'}


class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
                    
              
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None,**extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    
    languages_known=models.CharField(max_length=50)
    
    phoneNo = models.BigIntegerField(max_length = 15, error_messages={'required': 'Enter a valid Phone Number'})
    loginTimes = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['languages_known','first_name','phoneNo','loginTimes','points']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])
        
'''     
class User(models.Model):
    #userId = models.PositiveIntegerField(default = 0) # do not use userID 0 while assigning 
    username = models.EmailField(max_length=254)
    password = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    phoneNo = models.PositiveIntegerField(default = 0)
    languages = SeparatedValuesField(max_length = 254, token = ',')# models.CharField() 
    loginTimes = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
''' 

class Language(models.Model):
    #langId = models.IntegerField()
    langName = models.CharField(max_length = 30)
    def __unicode__(self):
        return self.langName

class Book(models.Model):
    #bookId = models.PositiveIntegerField(default = 0) #do not use bookId 0 while assigning 
    #add field for number of chunks
    lang = models.ForeignKey(Language)
    author = models.CharField(max_length=200)
    bookName = models.CharField(max_length=200)
    percentageCompleteAudio = models.FloatField(default = 0)
    percentageCompleteDigi = models.FloatField(default = 0)
    percentageAudioInvalid = models.FloatField(default = 0)
    dBookDownloads = models.PositiveIntegerField(default = 0)
    aBookDownloads = models.PositiveIntegerField(default = 0)
    numberOfChunks = models.PositiveIntegerField(default = 0)
    shouldConcatAudio = models.BooleanField(default = False)
    shouldConcatDigi = models.BooleanField(default = False)
    def __unicode__(self):
        return self.author + ',' + self.bookName + ',' + self.lang.langName

class Paragraph(models.Model):
    book = models.ForeignKey(Book)
    #paraId = models.PositiveIntegerField(default = 0)
    audioAssignedTo = models.ForeignKey(CustomUser, related_name = 'audioAssignedTo', default= None, blank = True, null = True)
    audioReadBy = models.ForeignKey(CustomUser, related_name = 'audioReadBy', default= None, blank = True, null = True)
    isRecording = models.BooleanField(default = False)
    digiAssignedTo = models.ForeignKey(CustomUser, related_name = 'digiAssignedTo', default= None, blank = True, null = True)
    digiBy = models.ForeignKey(CustomUser, related_name = 'digiBy', default= None, blank = True, null = True)
    isDigitizing = models.BooleanField(default = False)
    isChapter = models.BooleanField(default = False)
    validAudioVersionNumber = models.PositiveIntegerField(default = 0)
    upVotes = models.PositiveIntegerField(default = 0)
    downVotes = models.PositiveIntegerField(default = 0)
    status = models.CharField(max_length = 2, choices = (('re', 'Recording'),('va', 'Validating'),('do', 'Done')))
    
def concat(book_id):
    para_no = Paragraph.objects.filter(book=Book.objects.get(pk=book_id))
    infiles_list = []
    all_files_list = []
    offset=1;
    for i in para_no:
        file_name = str(book_id) + "/chunks/" + str(i.id) + "/DigiFiles/1.txt"
        if ((i.isChapter == 1)|(offset==1)):
            infiles_list = []
        infiles_list.append(file_name)
        if(offset<=len(para_no)-1):
            if (para_no[offset].isChapter==1):
                all_files_list.append(infiles_list)
        if(offset==len(para_no)):
            all_files_list.append(infiles_list)
        offset=offset+1

    #print("all_files_list")
    #print(all_files_list)
    return all_files_list


def pdfGen(Input,fontName,Output):
    pdf = FPDF()
    pdf.add_page()
    ttfName=fontName+'.ttf'
    pdf.add_font(fontName, '', ttfName, uni=True) 
    pdf.set_font(fontName, '', 14)
    linestring = open(Input, 'r').read()
    pdf.write(8,linestring)
    pdf.ln(20)
    pdf.output(Output, 'F')

    
def digiConcatenation(book_id):
    all_files_list=concat(book_id)
    count=1;
    Lang=Book.objects.get(pk = book_id).lang.langName
    #Lang=Language.objects.get(id=(Book.objects.get(pk = book_id)).lang).langName
    for i in all_files_list:
        for j in i:
            a = default_storage.open(j)
            path_to_save='/tmp/digiFiles/'
            local_fs = FileSystemStorage(location=path_to_save)
            local_fs.save(a.name,a)
    
        # all chapters: For each chapter one final1, final2.txt ..and corresponding pdf.
    for i in all_files_list:  
        path_final='/tmp/digiFiles/'+str(book_id)+'/'+str(count)+'.txt'
        with open(path_final, 'w') as fout:     
            # each chapter ka chunk
            for j in i:   
                temp='/tmp/digiFiles/'+j
                ins = open( temp, "r" )
                for line in ins:
                    fout.write(line)
                fout.write('\n\n')
        path_pdf='/tmp/digiFiles/'+str(book_id)+'/'+str(count)+'.pdf'
        '''
        langVar=fontLanguageMap[Lang]	
        if(langVar != ""):		
            pdfGen(path_final,fontLanguageMap[Lang],path_pdf)
            f = open(path_pdf, 'rb')
            myfile = File(f)
            new_name =str(book_id) + "/DigiChapters/Chapter"+str(count)+".pdf"
            default_storage.save(new_name,myfile)			 
        else:
		'''
        f = open(path_final, 'rb')
        myfile = File(f)
        new_name =str(book_id) + "/DigiChapters/Chapter"+str(count)+".txt"
        default_storage.save(new_name,myfile)    		
        
        os.remove(path_final)
        #os.remove(path_pdf)
        #local_fs.delete(path_final)
        count=count+1
        #fout.write('\f')   
    #path='/tmp/digiFiles/'
    #os.remove(path)
    '''
    for i in all_files_list:        
        for j in i:
            temp='/tmp/digiFiles/'
            os.remove(temp)
    '''
#@receiver(pre_save, sender=Book)
#check for completion pre_save of Paragraph
def checkForCompletion(sender, **kwargs): 
    from wa.tasks import concatAudio
    log = logging.getLogger("wa")
    log.setLevel(10)
    log.info("In checkForCompletion")
    book = kwargs['instance']
    log.info("Coming after ndu")
    #log.info("right i am still coming")
    #log.info(sender)
    log.info("book_id: " + str(book.id))
    chunks = book.numberOfChunks
    log.info("chunks: " + str(chunks) + "percentageCompleteAudio: " + str(book.percentageCompleteAudio))
    if((chunks != 0) and (book.percentageCompleteAudio == chunks) and (book.shouldConcatAudio == True)):
        log.info("coming inside if condition. Going to call audioconcat")
        print("Going to call audio concat")
        #audioConcatenation(book.id) 
        #A high value for countdown is needed
        concatAudio.apply_async(args = [book.id], countdown = 360)
        book.shouldConcatAudio = False
        book.save()
        print("Calling Audio concat")
    if((chunks!= 0) and (book.percentageCompleteDigi == chunks) and (book.shouldConcatDigi == True)):
        book.shouldConcatDigi = False
        book.save()
        digiConcatenation(book.id)          
        print("Calling pdfGen")

post_save.connect(checkForCompletion, sender=Book)

class UserHistory(models.Model):
    user = models.ForeignKey(CustomUser, null = False)
    loginTime = models.DateTimeField(auto_now_add = True)
    logoutTime = models.DateTimeField(default = datetime.now())
    action = models.CharField(max_length = 2, choices = (('re','Recorded'),('di', 'Digitized'),('va', 'validateAudio'),('vd', 'validateDigi'),('up', 'uploadBook')))   
    paragraph = models.ForeignKey(Paragraph, default= None, blank = True, null = True)
    vote = models.CharField(max_length = 2, choices = (('up', 'UpVote'), ('do', 'DownVote')), default = None, blank = True, null = True)
    audioVersion = models.PositiveIntegerField(default = 0)
    uploadedBook = models.ForeignKey(Book, default= None, blank = True, null = True)
#autoincr??

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/')
