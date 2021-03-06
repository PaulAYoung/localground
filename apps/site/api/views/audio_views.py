from localground.apps.site.api import serializers, filters
from localground.apps.site import models
from localground.apps.site.api.views.abstract_views import MediaList, MediaInstance


class AudioList(MediaList):
    ext_whitelist = ['m4a', 'mp3', 'mp4', 'mpeg', '3gp', 'aif', 'aiff', 'ogg']
    serializer_class = serializers.AudioSerializer
    model = models.Audio


class AudioInstance(MediaInstance):
    serializer_class = serializers.AudioSerializer
    model = models.Audio
