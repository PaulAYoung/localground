from django.contrib.gis.db import models
from datetime import datetime 
    
class Field(models.Model):
    form = models.ForeignKey('prints.Form')
    col_name = models.CharField(max_length=255)
    col_alias = models.CharField(max_length=255)
    data_type = models.ForeignKey('prints.DataType')
    time_stamp = models.DateTimeField(default=datetime.now)
    display_width = models.IntegerField() #percentage
    
    #field to be displayed in viewer
    is_display_field = models.BooleanField(default=False)
    # temporary stop gap:  whether or not to display the field in the
    # paper print form:
    is_printable = models.BooleanField(default=True)
    has_snippet_field = models.BooleanField(default=True)
    
    #how the fields should be ordered in the data entry form:
    ordering = models.IntegerField()
    
    def to_dict(self):
        return dict(alias=self.col_alias, width_pct=self.display_width)
    
    class Meta:
        app_label = "prints"
        ordering = ['form__id', 'ordering']
