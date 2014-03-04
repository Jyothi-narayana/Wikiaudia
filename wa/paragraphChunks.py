'''
	Input the userID and whether the paragraph should 
	be given for recording or digitization 
'''
from wa.models import Paragraph,CustomUser,Book
import logging
def getChunkID(userID,bookID,type):
	try:   
		log = logging.getLogger("wa")
		log.info("Coming into try block")
		cu = CustomUser.objects.get(pk=userID)
		book_instance = Book.objects.get(pk=bookID)
		if type is 0:
			chunks_assigned_to_user =  Paragraph.objects.filter(book=book_instance
				).filter(audioAssignedTo_id=userID
				).filter(audioReadBy_id__isnull=True)
		else:
			chunks_assigned_to_user = Paragraph.objects.filter(book=book_instance
				).filter(digiAssignedTo_id=userID
				).filter(digiBy_id__isnull=True)
		if len(chunks_assigned_to_user) is not 0:
			'''
					If a chunk which is assigned to user is found
					but is not recorded send the first available row 
					back to the user
			'''
			return chunks_assigned_to_user[0].id
		else:
			'''
				Assign a range to the user according to window size
			'''
			#assigned_till_chunk_id = 
			#last_unread_para_id =         		     		
			window_size = 3
			if type == 0:				
				assignAudioWindow(window_size,bookID,userID)
				chunks_assigned_to_user =  Paragraph.objects.filter(book=book_instance
				).filter(audioAssignedTo_id=userID
				).filter(audioReadBy_id__isnull=True)
			else:
				assignDigitizeWindow(window_size,bookID,userID)
				chunks_assigned_to_user =  Paragraph.objects.filter(book=book_instance
				).filter(digiAssignedTo_id=userID
				).filter(digiBy_id__isnull=True)
			return chunks_assigned_to_user[0].id

	except Exception as e:
		print e.message
		return 0

def assignAudioWindow(window_size,bookID,userID):
	book_instance = Book.objects.get(pk=bookID)
	chunk = Paragraph.objects.filter(book=book_instance
				).filter(audioReadBy_id__isnull=True)
	chunk_assigned = chunk.filter(audioAssignedTo_id__isnull=True)

	if len(chunk_assigned)==0:
		i=0
		for c in chunk:
			if i<window_size:
				c.audioAssignedTo_id =  userID
			else:
				c.audioAssignedTo_id = 0
			i = i+1
			c.save()
	else:
		i = 0
		for c in chunk_assigned:
			if i<window_size:
				chunkId = c.id;
				c.audioAssignedTo_id = userID;
				c.save()
				i=i+1
			else:
				break

def assignDigitizeWindow(window_size,bookID,userID):
	book_instance = Book.objects.get(pk=bookID)
	chunk = Paragraph.objects.filter(book=book_instance
				).filter(digiBy_id__isnull=True)
	chunk_assigned = chunk.filter(digiAssignedTo_id__isnull=True)

	if len(chunk_assigned)==0:
		i=0
		for c in chunk:
			if i<window_size:
				c.digiAssignedTo_id =  userID
			else:
				c.digiAssignedTo_id = 0
			i = i+1
			c.save()
	else:
		i = 0
		for c in chunk_assigned:
			if i<window_size:
				chunkId = c.id;
				c.digiAssignedTo_id = userID;
				c.save()
				i=i+1
			else:
				break

