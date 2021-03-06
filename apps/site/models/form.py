from django.contrib.gis.db import models
from django.db.models import Q
from localground.apps.site.managers import FormManager
from localground.apps.site.models import Field, ProjectMixin, \
    BaseNamed, Snippet, DataType, Project, BasePermissions
from localground.apps.site.dynamic import ModelClassBuilder, DynamicFormBuilder
from localground.apps.lib.helpers import get_timestamp_no_milliseconds
from django.db import transaction


class Form(BaseNamed, BasePermissions):
    slug = models.SlugField(
        verbose_name="Friendly URL",
        max_length=100,
        db_index=True,
        help_text='A few words, separated by dashes "-", to be used as part of the url',
        blank=False)
    table_name = models.CharField(max_length=255, unique=True)
    projects = models.ManyToManyField('Project')
    objects = FormManager()
    _model_class = None
    _data_entry_form_class = None

    class Meta:
        app_label = 'site'
        verbose_name = 'form'
        verbose_name_plural = 'forms'
        unique_together = ('slug', 'owner')

    def can_view(self, user=None, access_key=None):
        # check user it has object permissions:
        has_object_permissions = super(
            Form,
            self).can_view(
            user=user,
            access_key=access_key)
        if has_object_permissions:
            return True

        # if s/he doesn't, check if user has project permissions:
        for p in self.projects.all():
            if p.can_view(user=user, access_key=access_key):
                return True
        return False

    def can_edit(self, user):
        # check user it has object permissions:
        has_object_permissions = super(Form, self).can_edit(user)
        if has_object_permissions:
            return True

        # if s/he doesn't, check if user has project permissions:
        for p in self.projects.all():
            if p.can_edit(user):
                return True
        return False

    def can_manage(self, user):
        # check user it has object permissions:
        has_object_permissions = super(Form, self).can_manage(user)
        if has_object_permissions:
            return True

        # if s/he doesn't, check if user has project permissions:
        for p in self.projects.all():
            if p.can_manage(user):
                return True
        return False

    @classmethod
    def inline_form(cls, user):
        from localground.apps.site.forms import FormInlineUpdateForm
        return FormInlineUpdateForm

    @classmethod
    def get_form(cls):
        from localground.apps.site.forms import FormCreateForm
        return FormCreateForm

    @classmethod
    def sharing_form(cls):
        from localground.apps.site.forms import FormPermissionsForm
        return FormPermissionsForm

    @classmethod
    def create_form(cls, user):
        from localground.apps.site.widgets import TagAutocomplete
        from django.forms import ModelForm

        class InlineForm(ModelForm):

            def __init__(self, *args, **kwargs):
                super(InlineForm, self).__init__(*args, **kwargs)
                from localground.apps.site import models
                self.fields[
                    "projects"].queryset = models.Project.objects.get_objects(user)
                self.fields["projects"].help_text = 'Give one or more of your projects \
									access to this form.  Users who have access to the \
									projects you select will also have access to this form.'

            class Meta:
                from django import forms
                model = cls
                fields = ('name', 'description', 'tags', 'access_authority',
                          'slug', 'access_key', 'projects')
                widgets = {
                    'id': forms.HiddenInput,
                    'description': forms.Textarea(attrs={'rows': 3}),
                    'tags': TagAutocomplete(),
                    'projects': forms.widgets.CheckboxSelectMultiple
                }

        return InlineForm

    @classmethod
    def cache_dynamic_models(cls):
        from django.conf import settings
        # Add Dynamic Models to cache:
        # Useful link:  https://dynamic-models.readthedocs.org/en/latest/pdfindex.html?highlight=re
        # Not sure where to call this...probably in a try/except block
        from localground.apps.site.models import Form
        from django.db.models.loading import cache
        # the prefetch_related really cuts down on queries...but the DYNAMIC_MODELS_CACHED
        # flag isn't working!  Need to come up w/something else
        forms = Form.objects.prefetch_related(
            'field_set',
            'field_set__data_type').all()
        for form in forms:
            m = form.TableModel
            cache.app_models[
                m._meta.app_label][
                m._meta.object_name.lower()] = m

    def clear_table_model_cache(self):
        from django.db.models.loading import cache
        if cache.app_models['site'].get('form_%s' % self.id):
            del cache.app_models['site']['form_%s' % self.id]
        self._fields = None

    @property
    def TableModel(self):
        # This may be dangerous -- pretty sure the cache spans multiple
        # sessions.  If weird bugs appear, this is a suspect method
        '''from django.db.models.loading import cache
        if cache.app_models['site'].get('form_%s' % self.id) is None:
            cache.app_models['site'][
                'form_%s' %
                self.id] = ModelClassBuilder(self).model_class
        return cache.app_models['site']['form_%s' % self.id]
        '''
        return ModelClassBuilder(self).model_class

    def has_access(self, user, access_key=None):
        if self.access_authority.id == 3:
            return True
        elif self.access_authority.id == 2 and self.access_key == access_key:
            return True
        elif self.owner == user:
            return True
        else:
            from django.db.models import Q
            projects = self.projects.filter(Q(owner=user) |
                                            Q(users__user=user))
            return len(projects) > 0

    @property
    def DataEntryFormClass(self):
        if self._data_entry_form_class is None:
            dfb = DynamicFormBuilder(self)
            self._data_entry_form_class = dfb.data_entry_form_class
        return self._data_entry_form_class

    @classmethod
    def filter_fields(cls):
        from localground.apps.lib.helpers import QueryField, FieldTypes
        return [
            QueryField(
                'name',
                title='Name',
                operator='like'),
            QueryField(
                'description',
                title='Description',
                operator='like'),
            QueryField(
                'tags',
                title='Tags'),
            QueryField(
                'date_created',
                id='date_created_after',
                title='After',
                data_type=FieldTypes.DATE,
                operator='>='),
            QueryField(
                'date_created',
                id='date_created_before',
                title='Before',
                data_type=FieldTypes.DATE,
                operator='<=')]

    def sync_db(self):
        mcb = ModelClassBuilder(self)
        mcb.sync_db()

    def __unicode__(self):
        # return '%s - %s (%s)' % (self.id, self.name, self.table_name)
        return self.name

    def get_next_record(self, unverified_only=False, last_id=None):
        q = self.TableModel.objects.filter(snippet__is_blank=False)
        if unverified_only:
            q = q.filter(manually_reviewed=False)
        if last_id is not None:
            q = q.filter(id__gt=last_id)
        q = q.order_by('id', )
        if len(q) > 0:
            return q[0]

    @property
    def fields(self):
        if not hasattr(self, '_fields') or self._fields is None:
            self._fields = list(
                self.field_set.select_related('data_type').all()
                .order_by('ordering',)
            )
        return self._fields

    def get_fields(self, ordering='ordering', print_only=False):
        if print_only:
            fields = []
            for f in self.fields:
                if f.is_printable:
                    fields.append(f)
            return fields
        return self.fields

    def get_model_class(self):
        mcb = ModelClassBuilder(self)
        return mcb.model_class

    def save(self, user=None, *args, **kwargs):
        from localground.apps.lib.helpers import generic
        is_new = self.pk is None

        # 1. ensure that user doesn't inadvertently change the data type of the
        # column
        if is_new:
            if user and not hasattr(self, 'owner'):
                self.owner = user
            self.date_created = get_timestamp_no_milliseconds()
            self.table_name = 'table_%s_%s' % (
                self.owner.username, generic.generateID(num_digits=10))

        if user:
            self.last_updated_by = user
        self.time_stamp = get_timestamp_no_milliseconds()
        super(Form, self).save(*args, **kwargs)

        if is_new:
            self.sync_db()

    def get_num_field(self):
        dummy_num_field = Field()
        dummy_num_field.has_snippet_field = True
        dummy_num_field.col_name_db = 'num'
        dummy_num_field.col_alias = 'num'
        dummy_num_field.ordering = 0
        return dummy_num_field

    def get_snipped_field_names(self):
        names = ['num']
        for n in self.fields:
            names.append(n.col_name)
        return names

    def to_dict(self, print_only=True):
        return dict(
            id=self.id,
            name=self.name,
            columns=[
                f.to_dict() for f in self.get_fields(
                    print_only=print_only)])

    @transaction.commit_manually
    def add_records_batch(self, list_of_dictionaries, user):
        total_num = 0
        batch_num = 500
        counter = 0
        fields = self.fields
        for d in list_of_dictionaries:
            self.add_record(d, user, fields=fields)
            counter += 1
            if counter == batch_num:
                total_num += batch_num
                print('Committing the next %s records...' % batch_num)
                transaction.commit()
                print('Committed %s records total.' % total_num)
                counter = 0
        print('Committing the next %s records...' % batch_num)
        transaction.commit()
        print('Committed %s records total.' % total_num)

    def add_record(self, dictionary, user, fields=None):
        d = dictionary
        e = self.TableModel()
        if fields is None:
            print('querying for fields...')
            fields = self.fields

        # populate content that exists for all dynamic tables:
        e.snippet = d.get('snippet')
        e.project = d.get('project')
        e.num = d.get('num')
        e.num_snippet = d.get('num_snippet')
        e.time_stamp = get_timestamp_no_milliseconds()
        e.owner = user
        e.point = d.get('point')
        e.scan = d.get('scan')
        e.last_updated_by = d.get('last_updated_by')

        # populate ad hoc columns (variable across tables):
        for n in fields:
            e.__setattr__(n.col_name, d.get(n.col_name))
            e.__setattr__(
                '%s_snippet' %
                n.col_name,
                d.get(
                    '%s_snippet' %
                    n.col_name))
        e.save(user=user)
        self.save(user=user)
        return e

    def update_record(self, dictionary, user):
        d = dictionary
        e = self.TableModel.objects.get(id=int(d.get('id')))
        for k, v in d.items():
            e.__setattr__(k, v)
        e.save()

    def delete_record(self, id, user):
        self._delete_records([self.TableModel.objects.get(id=id)])

    def delete_records_by_ids(self, id_list, user):
        num_deletes = 0
        if len(id_list) > 0:
            objects = list(self.TableModel.objects.filter(id__in=id_list))
            num_deletes = self._delete_records(objects)
        return '%s records were deleted from the %s table.' % (
            num_deletes, self.name)

    def update_blank_status(self, id_list, user, blank_status):
        from django.forms.models import model_to_dict
        if len(id_list) > 0:
            recs = self.TableModel.objects.filter(id__in=id_list)
            snippet_ids = []
            for r in recs:
                # for each record, there are a number of snippet references.  Find
                # them so they can be update to blank / not blank:
                d = model_to_dict(r)
                for key, value in d.iteritems():
                    if key.find('snippet') != -1 and value is not None:
                        snippet_ids.append(value)
            Snippet.objects.filter(
                id__in=snippet_ids).update(
                is_blank=blank_status)
            return '%s records were updated from the %s table.' % (
                len(recs), self.name)
        return '0 records were deleted from the %s table.' % self.name

    def delete_record_by_snippet_id(self, snippet_id, user):
        num_deletes = 0
        if attachment_id is not None:
            try:
                objects = [self.TableModel.objects.get(snippet__id=snippet_id)]
                num_deletes = self._delete_records(objects)
            except self.TableModel.DoesNotExist:
                return 'A record corresponding to Snippet #%s in the %s table \
					does not exist.' % (snippet_id, self.name)
        return '%s records were deleted from the %s table.' % (
            num_deletes, self.name)

    def delete_records_by_attachment_id(self, attachment_id, user):
        num_deletes = 0
        if attachment_id is not None:
            objects = list(
                self.TableModel.objects .filter(
                    snippet__source_attachment__id=attachment_id))
            num_deletes = self._delete_records(objects)
        return '%s records were deleted from the %s table.' % (
            num_deletes, self.name)

    def _delete_records(self, records):
        from django.forms.models import model_to_dict
        num_deletes, snippet_ids = 0, []
        for r in records:
            # for each record, there are a number of snippet references.  Find
            # them so they can be deleted!
            d = model_to_dict(r)
            for key, value in d.iteritems():
                if key.find('_snippet') != -1 and value is not None:
                    snippet_ids.append(value)
            r.delete()
            num_deletes = num_deletes + 1
        Snippet.objects.filter(id__in=snippet_ids).delete()
        return num_deletes

    def source_table_exists(self):
        from django.db import connection, transaction
        try:
            table_name = self.table_name
            cursor = connection.cursor()
            cursor.execute('select count(id) from  %s' % table_name)
            # if no error raised then table exists:
            return True
        except Exception:
            # Table doesn't exist
            transaction.rollback_unless_managed()
            return False

    def delete(self, destroy_everything=True, **kwargs):
        if destroy_everything:
            # drop the underlying table if it exists:
            if self.source_table_exists():
                from django.db import connection
                cursor = connection.cursor()
                cursor.execute('drop table %s' % self.table_name)

        # remove referenced ContentType
        try:
            from django.contrib.contenttypes.models import ContentType
            ct = ContentType.objects.get(name='form_%s' % self.id)
            ct.delete()
        except ContentType.DoesNotExist:
            pass

        super(Form, self).delete(**kwargs)
