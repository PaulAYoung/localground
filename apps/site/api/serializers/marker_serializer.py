from localground.apps.site.api.serializers.base_serializer import GeometrySerializer
from localground.apps.site.api.serializers.form_serializer import create_record_serializer
from rest_framework import serializers
from localground.apps.site import models, widgets
from localground.apps.site.api import fields
from django.conf import settings


class MarkerSerializer(GeometrySerializer):
    
    def __init__(self, *args, **kwargs):
        super(MarkerSerializer, self).__init__(*args, **kwargs)
        self.records = []
    
    geometry = fields.GeometryField(
        help_text='Assign a GeoJSON string',
        required=False,
        widget=widgets.JSONWidget,
        geom_types=[
            'Point',
            'LineString',
            'Polygon'])
    children = serializers.SerializerMethodField('get_children')
    color = fields.ColorField(required=False)
    form_ids = serializers.SerializerMethodField('get_form_ids')
    photo_count = serializers.SerializerMethodField('get_photo_count')
    audio_count = serializers.SerializerMethodField('get_audio_count')
    map_image_count = serializers.SerializerMethodField('get_map_image_count')
    record_count = serializers.SerializerMethodField('get_record_count')

    class Meta:
        model = models.Marker
        fields = GeometrySerializer.Meta.fields + \
            ('children', 'color', 'form_ids', 'photo_count', 'audio_count', 'record_count', 'map_image_count')
        depth = 0

    def get_form_ids(self, obj):
        return obj.get_form_ids()

    def get_children(self, obj):
        # ~21 queries per marker is the best I can do if data from 2 separate
        # forms is attached to a single marker.  This query could be optimized
        # further if needed.
        from django.contrib.contenttypes.models import ContentType
        from localground.apps.site import models

        candidates = [
            models.Photo,
            models.Audio,
            models.Scan,
            models.Project,
            models.Marker]
        forms = (
            models.Form.objects .prefetch_related(
                'field_set',
                'field_set__data_type',
                'projects') .filter(
                projects=obj.project))
        for form in forms:
            candidates.append(form.TableModel)

        # this caches the ContentTypes so that we don't keep executing one-off
        # queries
        ContentType.objects.get_for_models(*candidates, concrete_model=False)
        children = {}
        self.audio = self.get_audio(obj) or []
        self.photos = self.get_photos(obj) or []
        self.map_images = self.get_map_images(obj) or []
        if self.audio:
            children['audio'] = self.audio
        if self.photos:
            children['photos'] = self.photos
        if self.map_images:
            children['map_images'] = self.map_images

        # add table data:
        form_dict = obj.get_records(forms=forms).items()
        for form, records in form_dict:
            SerializerClass = create_record_serializer(form)
            self.records.extend(records)
            d = self.serialize_list(
                obj,
                form.TableModel,
                SerializerClass(records).data,
                name=form.name,
                overlay_type='record',
                model_name_plural='form_%s' % form.id
            )
            d.update({
                'headers': [f.col_alias for f in form.fields]
            })
            children['form_%s' % form.id] = d

        return children

    def get_photos(self, obj):
        from localground.apps.site.api.serializers import PhotoSerializer

        data = PhotoSerializer(
            obj.photos,
            many=True,
            context={
                'request': self.request}).data
        return self.serialize_list(obj, models.Photo, data)

    def get_audio(self, obj):
        from localground.apps.site.api.serializers import AudioSerializer

        data = AudioSerializer(
            obj.audio,
            many=True,
            context={
                'request': self.request}).data
        return self.serialize_list(obj, models.Audio, data)

    def get_map_images(self, obj):
        from localground.apps.site.api.serializers import ScanSerializer

        data = ScanSerializer(
            obj.map_images,
            many=True,
            context={
                'request': self.request}).data
        return self.serialize_list(obj, models.Scan, data)
    
    def get_photo_count(self, obj):
        return len(obj.photos)

    def get_audio_count(self, obj):
        return len(obj.audio)

    def get_map_image_count(self, obj):
        return len(obj.map_images)

    def get_record_count(self, obj):
        return len(self.records)

    def serialize_list(self, obj, cls, data, name=None, overlay_type=None,
                       model_name_plural=None):
        if data is None or len(data) == 0:
            return None
        if name is None:
            name = cls.model_name_plural.title()
        if overlay_type is None:
            overlay_type = cls.model_name
        if model_name_plural is None:
            model_name_plural = cls.model_name_plural
        return {
            'id': model_name_plural,
            'name': name,
            'overlay_type': overlay_type,
            'data': data,
            'attach_url': '%s/api/0/markers/%s/%s/' %
            (settings.SERVER_URL,
             obj.id,
             model_name_plural)}


class MarkerSerializerCounts(GeometrySerializer):
    geometry = fields.GeometryField(
        help_text='Assign a GeoJSON string',
        required=False,
        widget=widgets.JSONWidget,
        geom_types=[
            'Point',
            'LineString',
            'Polygon'])
    color = fields.ColorField(required=False)
    photo_count = serializers.SerializerMethodField('get_photo_count')
    audio_count = serializers.SerializerMethodField('get_audio_count')
    map_image_count = serializers.SerializerMethodField('get_map_image_count')
    record_count = serializers.SerializerMethodField('get_record_count')
    update_metadata = serializers.SerializerMethodField('get_update_metadata')

    class Meta:
        model = models.Marker
        fields = GeometrySerializer.Meta.fields + \
            ('photo_count', 'audio_count', 'record_count', 'map_image_count', 'color',
             'update_metadata')
        depth = 0

    def get_photo_count(self, obj):
        try:
            return obj.photo_count
        except:
            return None

    def get_audio_count(self, obj):
        try:
            return obj.audio_count
        except:
            return None

    def get_map_image_count(self, obj):
        try:
            return obj.map_image_count
        except:
            return None

    def get_record_count(self, obj):
        try:
            return obj.record_count
        except:
            return None
        
    def get_update_metadata(self, obj):
        if self.request and self.request.method == 'POST':
            return self.metadata()
        return None
    
class MarkerSerializerLists(GeometrySerializer):
    geometry = fields.GeometryField(
        help_text='Assign a GeoJSON string',
        required=False,
        widget=widgets.JSONWidget,
        geom_types=[
            'Point',
            'LineString',
            'Polygon'])
    color = fields.ColorField(required=False)
    photo_array = serializers.SerializerMethodField('get_photo_count')
    audio_array = serializers.SerializerMethodField('get_audio_count')
    map_image_array = serializers.SerializerMethodField('get_map_image_count')
    record_array = serializers.SerializerMethodField('get_record_count')
    update_metadata = serializers.SerializerMethodField('get_update_metadata')

    class Meta:
        model = models.Marker
        fields = GeometrySerializer.Meta.fields + \
            ('photo_array', 'audio_array', 'record_array', 'map_image_array', 'color',
             'update_metadata')
        depth = 0

    def get_photo_count(self, obj):
        try:
            return obj.photo_array
        except:
            return None

    def get_audio_count(self, obj):
        try:
            return obj.audio_array
        except:
            return None

    def get_map_image_count(self, obj):
        try:
            return obj.map_image_array
        except:
            return None

    def get_record_count(self, obj):
        try:
            return obj.record_array
        except:
            return None
        
    def get_update_metadata(self, obj):
        if self.request and self.request.method == 'POST':
            return self.metadata()
        return None
