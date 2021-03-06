from rest_framework import serializers
from django.contrib.gis.geos import GEOSGeometry, GEOSException
from django.contrib.gis.gdal import OGRException
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import json

class GeometryField(serializers.WritableField):

    """
    A field to handle GeoDjango Geometry fields
    """
    type_label = 'geojson'
    type_name = 'GeometryField'
    geom_types = ['Point']
    point_field_name = 'point'
    polyline_field_name = 'polyline'
    polygon_field_name = 'polygon'
    nullable = False

    def __init__(self, *args, **kwargs):
        if kwargs.get('geom_types'):
            self.geom_types = kwargs.pop('geom_types')
        if kwargs.get('point_field_name'):
            self.point_field_name = kwargs.pop('point_field_name')
        if kwargs.get('polyline_field_name'):
            self.polyline_field_name = kwargs.pop('polyline_field_name')
        if kwargs.get('polygon_field_name'):
            self.polygon_field_name = kwargs.pop('polygon_field_name')

        # this is a hack because the required keyword doesn't seem to be
        # working
        if kwargs.get('required') != None:
            self.nullable = not kwargs.pop('required')

        super(GeometryField, self).__init__(*args, **kwargs)

    def field_from_native(self, data, files, field_name, into):
        geom = self.from_native(data.get(field_name))
        if geom is None:
            
            #if we can't null out the field, then do nothing:
            if not self.nullable:
                return None

            #...if we can null out the field, do it to the correct field:
            if 'Point' in self.geom_types:
                into[self.point_field_name] = None
            if 'LineString' in self.geom_types:
                into[self.polyline_field_name] = None
            if 'Polygon' in self.geom_types:
                into[self.polygon_field_name] = None
            return

        if geom.geom_type not in self.geom_types:
            raise serializers.ValidationError('Unsupported geometry type')

        # only one geom can exist at a time: Point, LineString, and Polygon
        # are mutually exclusive. Can't have more than one at once.
        if geom.geom_type == 'Point':
            point, polyline, polygon = geom, None, None
        elif geom.geom_type == 'LineString':
            point, polyline, polygon = None, geom, None
        elif geom.geom_type == 'Polygon':
            point, polyline, polygon = None, None, geom
        else:
            raise serializers.ValidationError('Unsupported geometry type')

        if 'Point' in self.geom_types:
            into[self.point_field_name] = point
        if 'LineString' in self.geom_types:
            into[self.polyline_field_name] = polyline
        if 'Polygon' in self.geom_types:
            into[self.polygon_field_name] = polygon

    def to_native(self, value):
        if value is not None:
            if isinstance(value, dict) or value is None:
                return value
            # Get GeoDjango geojson serialization and then convert it _back_ to
            # a Python object
            return json.loads(value.geojson)

    def from_native(self, value):
        if value is not None and value != '':
            try:
                return GEOSGeometry(value)
            except (ValueError, GEOSException, OGRException, TypeError) as e:
                raise serializers.ValidationError(
                        _('''Invalid format: "{0}"
                          unrecognized as WKT EWKT, and HEXEWKB.'''.format(value)))

            return value
        return None

