from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

'''
--------------------------------------------------------------------------------
On using different URL patterns to point to the same view:
https://docs.djangoproject.com/en/1.2/topics/http/urls/#naming-url-patterns
--------------------------------------------------------------------------------
EXCERPT:
It's fairly common to use the same view function in multiple URL patterns in your
URLconf.  This is completely valid, but it leads to problems when you try to do
reverse URL matching (through the permalink() decorator or the url template tag).
Continuing this example, if you wanted to retrieve the URL for the archive view,
Django's reverse URL matcher would get confused, because two URL patterns point
at that view.

To solve this problem, Django supports named URL patterns. That is, you can give
a name to a URL pattern in order to distinguish it from other patterns using the
same view and parameters. Then, you can use this name in reverse URL matching.
--------------------------------------------------------------------------------
'''
    
handler500 = 'localground.account.views.server_error' 
urlpatterns = patterns('',
    #(r'^404/', direct_to_template, {'template': '404.html'}),
    (r'^$', direct_to_template, {'template': 'splash.html'}),
    (r'^about/$', direct_to_template, {'template': 'about.html'}),
    (r'^instructions/$', direct_to_template, {'template': 'instructions.html'}),
    (r'^research/$', direct_to_template, {'template': 'research.html'}),
    (r'^contact/$', direct_to_template, {'template': 'contact.html'}),
    (r'^credits/$', direct_to_template, {'template': 'credits.html'}),
    
    
    (r'^profile/', include('localground.account.urls')),
                       
    #disabling new user registration for now:
    (r'^accounts/', include('localground.registration.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    
    #api:
    (r'^api/0/tester/', include('localground.api.urls.tester_urls')),
    (r'^api/0/', include('localground.api.urls.api_urls')),
    
    #todo:  is this section even needed?  Need to understand it better:
    #(r'^admin/', include(admin.site.urls)),
    
    #print:
    #(r'^$', 'localground.prints.views.configure_print'), #change to splash page
    (r'^print/', include('localground.prints.urls')),
    
    #EBAYS:
    (r'^ebays/', include('localground.ebays.urls')),
    
    #upload:  manages the forms-based uploader:
    (r'^upload/$', 'localground.uploads.views.uploader.init_upload_form'),
    (r'^upload/embed/$', 'localground.uploads.views.uploader.init_upload_form', {
        'embed': True,
        'base_template': 'twitter/iframe.html'
    }),
    #(r'^upload/media/$', 'localground.uploads.views.uploader.init_media_form'),
    #(r'^upload/post/$', 'localground.uploads.views.uploader.upload'),
    (r'^upload/media/post/$', 'localground.uploads.views.uploader.upload_media'),
    
    #overlays
    (r'^overlays/save-marker/$', 'localground.overlays.views.save_marker'),
    (r'^overlays/delete-marker/$', 'localground.overlays.views.delete_marker'),
    (r'^overlays/show-marker/$', 'localground.overlays.views.show_marker_detail'),
    (r'^overlays/show-marker/embed/$', 'localground.overlays.views.show_marker_detail',
    {
        'embed': True,
        'base_template': 'twitter/iframe.html'
    }),
    
    
    #(r'^multimedia/$', 'localground.multimedia.views.init_upload_form'),
    
    #manages scan processing and viewing (the python script posts here):
    (r'^scans/', include('localground.uploads.urls')),
    #(r'^scan/(?P<scan_id>\w+)/', 'localground.viewer.views.show_scan'),
    
    #map viewer:
    #(r'^viewer/', include('localground.viewer.urls')),
    (r'^maps/', include('localground.viewer.urls')),
    
    #download:
    #(r'^download/kml/print/(?P<print_id>\w+)/', 'localground.viewer.views.download_kml'),
    
    #testing:
    #(r'^html5/', 'localground.test.views.html5_test'),
    #(r'^sliders/', 'localground.test.views.sliders_test'),
    #(r'^adjust/', 'localground.test.views.adjust_color'),
    
    #django-tagging:
    url(r'^tagging_autocomplete/list/json$', 'tagging_autocomplete.views.list_tags',
                                            name='tagging_autocomplete-list'),
)

#for Varun:
'''
if settings.DEBUG:
     urlpatterns += patterns('',
         (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
             {'document_root': settings.MEDIA_ROOT}),
     )
'''