from django.contrib.gis.db import models
from localground.apps.site.models.abstract.base import Base


class Layout(Base):
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, blank=True)
    map_width_pixels = models.IntegerField()
    map_height_pixels = models.IntegerField()
    qr_size_pixels = models.IntegerField()
    border_width = models.IntegerField()
    is_active = models.BooleanField(default=True)
    is_landscape = models.BooleanField(default=False)
    is_data_entry = models.BooleanField(default=True)
    is_mini_form = models.BooleanField(default=False)

    class Meta:
        app_label = 'site'
        ordering = ('id',)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'map_width': self.map_width_pixels,
            'map_height': self.map_height_pixels
        }

    def __unicode__(self):
        return '%s. %s' % (self.id, self.display_name)
