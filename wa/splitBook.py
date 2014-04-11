from __future__ import division
from PIL import Image as Image2
import math
import cv2
import numpy as np
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from wand.image import Image
from wa.models import Book
from wa.models import Language,Book, Paragraph, UserHistory, Document
#import wikiaudia.settings
import re,os,sys
import logging


def halve_page(image_path, out_name, outdir, slice,book_id):
    print ("Inside Halve_page")
    print(image_path)   
    #print(slice_list)
    with open(str(image_path), 'rb') as f:
        myfile = File(f)
        img = Image2.open(f)
        print img.size
        width, height = img.size
        print(width)
        print(height)
        working_slice = img.crop((0, 0,width,slice))
        print working_slice
        #working_slice.save(os.path.join(outdir, image_path+"slice_" + out_name + "_1.png"))        
        working_slice.save(os.path.join(outdir,"1.png"))    
        with open("1.png", 'rb') as f1:
            myfile1=File(f1)            
            para = Paragraph(book = Book.objects.get(pk = book_id), status = 're')
            para.save()
            path_to_save = str(book_id) + "/chunks/" + str(para.id) + "/image.png"                      
            print "para ID: " + str(para.id)
            default_storage.save(path_to_save, myfile1)         
      
   
        working_slice = img.crop((0, slice,width,height))
        working_slice.save(os.path.join(outdir,"1.png"))
        with open("1.png", 'rb') as f1:
            myfile1=File(f1)            
            para = Paragraph(book = Book.objects.get(pk = book_id), status = 're')
            para.save()
            path_to_save = str(book_id) + "/chunks/" + str(para.id) + "/image.png"                      
            print "para ID: " + str(para.id)
            default_storage.save(path_to_save, myfile1)         
    
    #working_slice.save(os.path.join(outdir, image_path+"slice_" + out_name + "_2.png"))
   
def most_common(lst):
    return max(set(lst), key=lst.count)

def check_line(i,y,mined_list,mode_line_length):
    for j in range(8):
        if i< len(mined_list):
            if (((mined_list[i][0]>=y-3)&(mined_list[i][0]<=y+3))&(mined_list[i][2]>=(mode_line_length - 10 ))):
                return True
            i=i+1
        else :
            return False
    return False

def long_slice(image_path, out_name, outdir, slice_list,book_id):
    print ("Inside Halve_page")
    print(image_path)   
    print(slice_list)   
    with open(str(image_path), 'rb') as f:
        myfile = File(f)
        img = Image2.open(f)    
        #img = Image2.open(image_path)
        #print img.size
        width, height = img.size
        print(width)
        print(height)
        upper = 0
        left = 0
        lower=slice_list[0]
        count = 1
        for slice in range(0,len(slice_list)+1):
            
            if lower== slice_list[len(slice_list)-1]:
                lower = height
            else:
                lower = slice_list[slice]  
            bbox = (left, upper, width, lower)
            working_slice = img.crop(bbox)
            if lower!=height:
                upper = slice_list[slice]
            working_slice.save(os.path.join(outdir,"1.png"))
            with open("1.png", 'rb') as f1:
                myfile1=File(f1)            
                para = Paragraph(book = Book.objects.get(pk = book_id), status = 're')
                para.save()
                path_to_save = str(book_id) + "/chunks/" + str(para.id) + "/image.png"                      
                print "para ID: " + str(para.id)
                default_storage.save(path_to_save, myfile1) 
            count +=1
        
def Split_to_para(image_path,book_id):
    noChunks=0
  
    img = cv2.imread(image_path)
    cnt = 0
    height, width, depth = img.shape;
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    lines = cv2.HoughLinesP(edges,1,np.pi/180,40,minLineLength = width/32, maxLineGap = 1000)

    mined_list=[]
    line_length=[]
    start_point=[] #x1's
    end_point=[]
    for x1,y1,x2,y2 in lines[0]:
        if (abs(y2-y1) < 12):
            cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
            cnt += 1
            sub_tuple=(y1,x1,(x2-x1))
            mined_list.append(sub_tuple)
            line_length.append((x2-x1))
            start_point.append(x1)
            end_point.append(x2)
                  
    mined_list.sort(key=lambda tup: tup[0])
    mode_line_length= most_common(line_length)
    mode_start_point= most_common(start_point)
    mode_end_point= most_common(end_point)
    count=0
    possible_cutline =[] # blue lines
    for i in mined_list:
        count=count+1
        if ((i[2] < mode_line_length - 10)& ((i[1]>= (mode_start_point - 10)) & (i[1]<=(mode_start_point +10))) ):
           if check_line(count-4,i[0],mined_list,mode_line_length)==False:
                cv2.line(img,(i[1],i[0]),(i[1]+i[2],i[0]),(255,0,0),2)
                possible_cutline.append(i)

    possible_cutline.sort(key=lambda tup: tup[0])
   
    if (len(possible_cutline) >0 ):
        final_cutline=[possible_cutline[len(possible_cutline)-1][0]]
        i=0
        support_list=[]
        while i <= len(possible_cutline)-2 :
            support_list.append(possible_cutline[i+1][0]-possible_cutline[i][0])
            i=i+1
 
        i=0
        while i <= len(support_list)-1:
            if( (i<len(possible_cutline)) & (support_list[i] > 50)) :
               final_cutline.append(possible_cutline[i][0])
            i=i+1
        
        temp=height-(height/10)
        for i in final_cutline:
            if i>=temp:
                final_cutline.remove(i)

        final_cutline[:] = [x + 8 for x in final_cutline]

        final_cutline.sort()
        i=0
        temp=height/10
        while i <= len(final_cutline)-2:
            if((final_cutline[i+1]-final_cutline[i]) <= temp):
                final_cutline.pop(i+1)
            i=i+1
        temp=len(final_cutline)
        noChunks=temp+1     
        print("no_chunks form split+para")
        print(noChunks)     
        if temp != 1:
            long_slice(image_path,"slices", os.getcwd(), final_cutline,book_id)
        else:
            halve_page(image_path,"slices", os.getcwd(), final_cutline[0],book_id)
    else:
        noChunks=1  
        with open(str(image_path), 'rb') as f:
            myfile = File(f)
            img = Image2.open(f)
            outdir=os.getcwd()          
            img.save(os.path.join(outdir,"1.png"))  
            with open("1.png", 'rb') as f1:
                myfile1=File(f1)            
                para = Paragraph(book = Book.objects.get(pk = book_id), status = 're')
                para.save()
                path_to_save = str(book_id) + "/chunks/" + str(para.id) + "/image.png"                      
                print "para ID: " + str(para.id)
                default_storage.save(path_to_save, myfile1)         
    return noChunks         
    
def splitBookIntoPages(f_arg, book_id):
    #print 'splitbook'
    rxcountpages = re.compile(r"$\s*/Type\s*/Page[/\s]", re.MULTILINE|re.DOTALL)
    noChunks=0;
    #--TODOJO--Change this depending on your system path
    sys.path.append('/home/jo/wikiaudia/')
    #sys.path.append('/home/jo/wikiaudia/wa/')
    os.environ['DJANGO_SETTINGS_MODULE']='wikiaudia.settings'
    log = logging.getLogger("wa")
    log.info("hiiii")
    log.info(f_arg)
    print f_arg
    print "Before IF"
    if default_storage.exists(f_arg):
        print "splitbook file exists"
        a = default_storage.open(f_arg)
        
        local_fs = FileSystemStorage(location='/tmp/pdf')
        local_fs.save(a.name,a)
        mod_path = "/tmp/pdf/"+ f_arg
        print mod_path
        #default_storage.close(f_arg)
        data = file(mod_path,"rb").read()
        #log.info(file(mod_path,"rb").size())
        no_pages = len(rxcountpages.findall(data))
        file_for = mod_path+"[%d]"
        #--TODOJO--save the image in the path as required. Cuurently just stores as temp[i]. 
        print no_pages
        continueConversion = True
        i = 0
        _img = Image(filename=file_for)
        while continueConversion:
            
            filen = file_for%i
            try:
                with Image(filename=filen) as img:
                    if img:
                        print type(img)
                        img.save(filename=("temp[%d].png"%i))
                    else:
                        print("false")
                        continueConversion = False


                with open("temp[%d].png"%i, 'rb') as f:
                    
                    myfile = File(f)
                    if i==0:
                        path_to_save= str(book_id)+"/bookThumbnail.png"
                        default_storage.save(path_to_save, myfile)
                    ''' 
                    else:
                        myfile.close()
                        Split_to_para("temp[%d].png"%i,book_id)
                    ''' 
                    myfile.close()
                    
                    noChunks=noChunks+Split_to_para("temp[%d].png"%i,book_id)
                    print("no_chunks form book +split")
                    print(noChunks)     
                    os.remove("temp[%d].png"%i)
                i=i+1
            except Exception, e:
                print "Couldn't do it: %s" % e
                print ("coming to except")
                break
        print "-------------------"
        print i
        #update book table to add number of chunks
        book = Book.objects.get(pk = book_id)
        book.numberOfChunks = noChunks
        book.save()
        os.remove(mod_path)
        
    else:
        print "doesn't exist"

def to_infinity():
    index = 0
    while 1: 
        yield index
        index += 1


    '''
    data = file(f_arg,"rb").read()
    no_pages = len(rxcountpages.findall(data))
    file_for = f_arg+"[%d]"
    for i in range(0,2):
        filen = file_for%i
        with Image(filename=filen) as img:
            img.save(filename=("temp[%d].jpg"%i))
    '''
