from django.shortcuts import render_to_response
from localground.apps.site.models import *
from localground.apps.helpers import generic
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from localground.apps.site.decorators import process_identity, process_project
from django.conf import settings
from django.template import RequestContext
import simplejson as json
from localground.apps.site.models import Project
from datetime import datetime


@process_project  
@login_required
def init_upload_form(request,
                 template_name='forms/uploader.html',
                 base_template='base/base.html',
                 embed=False, identity=None, project=None):
    username = identity.username if identity is not None else 'all'
    projects = Project.objects.get_objects(identity)
    if request.user.is_superuser and username == 'all':
        projects = Project.objects.all().order_by('name')
    project_id = 'all'
    if project is not None: project_id = str(project.id)
    extras = {
        'embed': embed,
        'base_template': base_template,
        'projects': projects,
        'selected_project': project,
        'selected_project_id': project_id
    }
    return render_to_response(template_name, extras,
                              context_instance = RequestContext( request))


@process_project 
@login_required
def upload_media(request, object_type_plural, project=None):
    if request.method == 'POST':
        new_object, message = None, None
        #branch processing based on upload type:
        file = request.FILES.get('files[]')   
        ModelClass = Base.get_model_from_plural_object_type(object_type_plural)
        media_object = ModelClass()
        media_object.save_upload(file, request.user, project)
        responseObj = {
            'fileName': new_object.file_name_orig,
            'user': identity.username,
            'content_type': new_object.content_type,
            'time_created': datetime.now().strftime('%m/%d/%Y, %I:%M %p'),
            'update_url': '/profile/%s/?project_id=%s' % \
                                (new_object.get_object_type(), project.id),
            'delete_url': '/profile/%s/delete/%s/' % \
                        (new_object.get_object_type(), new_object.id)
        }
        return HttpResponse(json.dumps(responseObj))
    else:
        return HttpResponse(json.dumps(dict(message='Not a post')))
