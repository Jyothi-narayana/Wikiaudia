from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from wand.image import Image
from wa.models import Book
#import wikiaudia.settings
import re,os,sys
def splitBookIntoPages(f_arg):
	#print 'splitbook'
	rxcountpages = re.compile(r"$\s*/Type\s*/Page[/\s]", re.MULTILINE|re.DOTALL)
	#--TODOJO--Change this depending on your system path
	sys.path.append('/home/pc/Documents/finalyear/jo/Wikiaudia')
	os.environ['DJANGO_SETTINGS_MODULE']='wikiaudia.settings'

	if default_storage.exists(f_arg):
		print "splitbook file exists"
		a = default_storage.open(f_arg)
		local_fs = FileSystemStorage(location='/tmp/pdf')
		local_fs.save(a.name,a)
		mod_path = "/tmp/pdf/"+a.name
		data = file(mod_path,"rb").read()
		no_pages = len(rxcountpages.findall(data))
		file_for = mod_path+"[%d]"
		#--TODOJO--save the image in the path as required. Cuurently just stores as temp[i]. 
		print no_pages
		for i in range(0,no_pages):
			filen = file_for%i
			with Image(filename=filen) as img:
				if img:
					print type(img)
					img.save(filename=("temp[%d].jpg"%i))
				else:
					break;
			with open("temp[%d].jpg"%i, 'r') as f:
				myfile = File(f)
				default_storage.save("temp[%d].jpg"%i,myfile)
				os.remove("temp[%d].jpg"%i)
				#close file


	'''
	data = file(f_arg,"rb").read()
	no_pages = len(rxcountpages.findall(data))
	file_for = f_arg+"[%d]"
	for i in range(0,2):
		filen = file_for%i
		with Image(filename=filen) as img:
			img.save(filename=("temp[%d].jpg"%i))
	'''
