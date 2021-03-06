from localground.apps.site.api.serializers.base_serializer import BaseNamedSerializer
from localground.apps.site.api.serializers.field_serializer import FieldSerializer
import datetime
from django.conf import settings
from rest_framework import serializers
from localground.apps.site import widgets, models
from localground.apps.site.api import fields
from django.http import HttpResponse


class FormSerializerList(BaseNamedSerializer):
    project_ids = fields.ProjectsField(
        label='project_ids',
        source='projects',
        required=True,
        help_text='A comma-separated list of all of the projects to which this form should belong'
    )
    data_url = serializers.SerializerMethodField('get_data_url')

    class Meta:
        model = models.Form
        fields = BaseNamedSerializer.Meta.fields + ('data_url', 'project_ids')
        depth = 0

    def get_data_url(self, obj):
        return '%s/api/0/forms/%s/data/' % (settings.SERVER_URL, obj.pk)


class FormSerializerDetail(FormSerializerList):
    fields = serializers.SerializerMethodField('get_form_fields')

    class Meta:
        model = models.Form
        fields = FormSerializerList.Meta.fields + ('fields',)
        depth = 0

    def get_form_fields(self, obj):
        return FieldSerializer(
            obj.fields, many=True,
            context={'request': {}}).data

# BaseNamedSerializer?


class BaseRecordSerializer(serializers.ModelSerializer):

    geometry = fields.GeometryField(help_text='Assign a GeoJSON string',
                                    required=False,
                                    widget=widgets.JSONWidget)
    overlay_type = serializers.SerializerMethodField('get_overlay_type')
    url = serializers.SerializerMethodField('get_detail_url')
    project_id = fields.ProjectField(
        label='project_id',
        source='project',
        required=False)

    class Meta:
        fields = (
            'id',
            'overlay_type',
            'url',
            'geometry',
            'manually_reviewed',
            'project_id')
        read_only_fields = ('manually_reviewed',)

    def get_overlay_type(self, obj):
        return obj._meta.verbose_name

    def get_detail_url(self, obj):
        return '%s/api/0/forms/%s/data/%s/' % (settings.SERVER_URL,
                                               obj.form.id, obj.id)

def create_record_serializer(form):
    """
    generate a dynamic serializer from dynamic model
    """
    #from localground.apps.site.api.fields import TablePhotoField
    from localground.apps.site.api import fields
    field_names, photo_fields, photo_details, audio_fields, audio_details = [], [], [], [], []
    display_field = None
    for f in form.fields:
        if f.is_display_field:
            display_field = f
        field_names.append(f.col_name)
        if f.data_type.id == 7:
            photo_fields.extend([f.col_name, f.col_name + "_detail"])
        elif f.data_type.id == 8:
            audio_fields.extend([f.col_name, f.col_name + "_detail"])
    
    #append display name:
    if display_field is not None:
        field_names.append('display_name')   
    
    #append "num_field" column:
    field_names.append(form.get_num_field().col_name)
    
    TableModel = form.TableModel
    class Meta:
        model = TableModel
        fields = BaseRecordSerializer.Meta.fields + tuple(field_names) + \
            tuple(photo_fields) + tuple(audio_fields) 
        read_only_fields = BaseRecordSerializer.Meta.read_only_fields
    
    attrs = {
        '__module__': 'localground.apps.site.api.serializers.FormDataSerializer',
        'Meta': Meta
    }
    #set custom display name field getter, according on the display_field:
    if display_field is not None:
        attrs.update({
            'display_name': serializers.Field(source=display_field.col_name)
        })
        
    for f in photo_fields:
        if f.find("_detail") != -1:
            source = f.replace("_detail", "")
            attrs.update({
                f: fields.TablePhotoJSONField(read_only=True, source=source)
            })
        else:
            model_field = TableModel()._meta.get_field(f)
            attrs.update({
                f: fields.CustomModelField(
                    type_label="photo",
                    model_field=model_field
                )
            })
    
    for f in audio_fields:
        if f.find("_detail") != -1:
            source = f.replace("_detail", "")
            attrs.update({
                f: fields.TableAudioJSONField(read_only=True, source=source)
            })
        else:
            model_field = TableModel()._meta.get_field(f)
            attrs.update({
                f: fields.CustomModelField(
                    type_label="audio",
                    model_field=model_field
                )
            })
    
    return type('record_serializer_default', (BaseRecordSerializer, ), attrs)

def create_compact_record_serializer(form):
    """
    generate a dynamic serializer from dynamic model
    """
    col_names = [f.col_name for f in form.fields]

    class FormDataSerializer(BaseRecordSerializer):
        recs = serializers.SerializerMethodField('get_recs')
        url = serializers.SerializerMethodField('get_detail_url')
        project_id = serializers.SerializerMethodField('get_project_id')

        class Meta:
            model = form.TableModel
            fields = (
                'id',
                'num',
                'recs',
                'url',
                'geometry',
                'project_id',
                'overlay_type')

        def get_recs(self, obj):
            # return [getattr(obj, col_name) for col_name in col_names]
            recs = []
            for col_name in col_names:
                val = getattr(obj, col_name)
                if isinstance(val, datetime.datetime):
                    val = val.strftime('%m/%d/%Y, %I:%M:%S %p')
                recs.append(val)
            return recs

        def get_detail_url(self, obj):
            return '%s/api/0/forms/%s/data/%s/' % (settings.SERVER_URL,
                                                   form.id, obj.id)

        def get_project_id(self, obj):
            return obj.project.id

        def get_overlay_type(self, obj):
            return 'record'

    return FormDataSerializer
