from django import test
from localground.apps.site.views import prints, profile
from localground.apps.site import models
from localground.apps.site.tests import ViewMixin
from rest_framework import status
		
class FormProfileTest(test.TestCase, ViewMixin):
	def setUp(self):
		ViewMixin.setUp(self)
		self.urls = ['/profile/forms/']
		self.view = profile.object_list_form