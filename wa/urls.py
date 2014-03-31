from django.conf.urls import patterns, url;
from wa import views;

urlpatterns = patterns('',
	url(r'^$', views.front, name='front'),
	#url(r'^contributeOut/$', views.contributeOut, name='contributeOut'),
	url(r'audio/bookParas/', views.bookParas, name='bookParas'),
	url(r'audio/getParaImage/(?P<book_id>\d+)/(?P<para_id>\d+)/', views.getParaImage, name = 'getParaImage'),
	url(r'audio/(?P<book_id>\d+)/(?P<para_id>\d+)/', views.chooseParaAction, name = 'chooseParaAction'),
	url(r'getAudio/(?P<book_id>\d+)/(?P<para_id>\d+)/', views.getAudio, name = 'getAudio'),
	url(r'upVoted/(?P<book_id>\d+)/(?P<para_id>\d+)/', views.upVoted, name = 'upVoted'),
	url(r'downVoted/(?P<book_id>\d+)/(?P<para_id>\d+)/', views.downVoted, name = 'downVoted'),
	
	url(r'audio/getimage/(?P<book_id>\d+)/', views.getImage, name = 'getImage'),
	url(r'audio/(?P<book_id>\d+)/', views.chooseAction, name = 'chooseAction'),
	url(r'^aboutUs/$', views.aboutUs, name='aboutUs'),
	url(r'^aboutUsOut/$', views.aboutUsOut, name='aboutUsOut'),
	
	url(r'audio/langBooks/', views.langBooks, name='langBooks'),
	url(r'audio/', views.audioSelection, name = 'audioSelection'),
	url(r'getParagraph/(?P<book_id>\d+)/(?P<para_id>\d+)/', views.getParagraph, name = 'getParagraph'),
	url(r'myprofile/', views.myprofile, name = 'myprofile'),
	url(r'userDetailsLangwise/', views.userDetailsLangwise, name = "userDetailsLangwise"),
                                                                         
    #url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
	url(r'^$', views.front, name='front'),
    url(r'^audioUpload/$', views.audioUpload, name='audioUpload'),
    url(r'^audioUploadForm/(?P<book_id>\d+)/(?P<para_id>\d+)/$', views.audioUploadForm, name='audioUploadForm'),
	url(r'^login/$', views.front, name='front'),

	url(r'^auth/$', views.auth_view, name='auth_view'),
	url(r'^home/$', views.home, name='home'),
	url(r'^register/$', views.register_user, name='register_user'),
	url(r'^register_success/$', views.register_success, name='register_success'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^digiSelection/$', views.digiSelection, name='digiSelection'),
	url(r'^uploadDigi/(?P<book_id>\d+)/(?P<para_id>\d+)/$', views.uploadDigi, name='uploadDigi'),
	url(r'^ajaxexample_json/$', views.ajax, name='ajax'),
	#url(r'^concatenate_digi/$', views.concatenateDigi, name='concatenateDigi'),
	url(r'^uploadBook/$', views.uploadBook, name='uploadBook'),
	url(r'^valSelection/$', views.valSelection, name='valSelection'),
)
