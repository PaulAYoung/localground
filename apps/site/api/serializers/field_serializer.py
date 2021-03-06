from rest_framework import serializers
from localground.apps.site import models
from django.conf import settings

class FieldSerializerBase(serializers.ModelSerializer):
    '''
    Hack: can't use HyperlinkSerializer field for URLs with two
    dynamic parameters because of DRF limitations. So, we'll build
    the URL for ourselves:
    '''
    url = serializers.SerializerMethodField('get_url')
    col_name = serializers.SerializerMethodField('get_col_name')
    
    class Meta:
        model = models.Field
        fields = ('id', 'form', 'col_alias', 'col_name', 'is_display_field',
                  'display_width', 'is_printable', 'has_snippet_field', 'ordering',
                  'data_type', 'url')
        
    def get_url(self, obj):
        return '%s/api/0/forms/%s/fields/%s' % \
                (settings.SERVER_URL, obj.form.id, obj.id)
        
    def get_col_name(self, obj):
        return obj.col_name

class FieldSerializer(FieldSerializerBase):
    #data_type = serializers.SlugRelatedField(slug_field='name')
    class Meta:
        model = models.Field
        read_only_fields = ( 'form', )
        fields = FieldSerializerBase.Meta.fields
    
class FieldSerializerUpdate(FieldSerializerBase):
    class Meta:
        model = models.Field
        read_only_fields = ( 'data_type', 'form')
        fields =  FieldSerializerBase.Meta.fields
