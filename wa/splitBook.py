from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from wand.image import Image
from wa.models import Book
from wa.models import Language,Book, Paragraph, UserHistory, Document
#import wikiaudia.settings
import re,os,sys
import logging
def splitBookIntoPages(f_arg, book_id):
	#print 'splitbook'
	rxcountpages = re.compile(r"$\s*/Type\s*/Page[/\s]", re.MULTILINE|re.DOTALL)

	#--TODOJO--Change this depending on your system path
	sys.path.append('/home/jo/wikiaudia/')
	#sys.path.append('/home/jo/wikiaudia/wa/')
	os.environ['DJANGO_SETTINGS_MODULE']='wikiaudia.settings'
	log = logging.getLogger("wa")
	#log.info("hiiii")
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
						continueConversion = False


				with open("temp[%d].png"%i, 'r') as f:
					myfile = File(f)
					if i==0:
						path_to_save= str(book_id)+"/bookThumbnail.png"
					else:
						para = Paragraph(book = Book.objects.get(pk = book_id), status = 're')
						para.save()
						path_to_save = str(book_id) + "/chunks/" + str(para.id) + "/image.png"						
						print "para ID: " + str(para.id)
					default_storage.save(path_to_save, myfile)
					os.remove("temp[%d].png"%i)
				i=i+1
			except:
				break
		print "-------------------"
		print i
		#update book table to add number of chunks
		book = Book.objects.get(pk = book_id)
		book.numberOfChunks = i-1
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
