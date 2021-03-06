import json
import logging
from urlparse import urljoin

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.http import QueryDict
from django.test import RequestFactory, TestCase, override_settings

from guardian.utils import get_anonymous_user
import mock
import requests
from rest_framework.test import (APIRequestFactory, APITestCase,
                                 force_authenticate)

from data_set_manager.models import Assay
from data_set_manager.search_indexes import NodeIndex
from factory_boy.utils import create_dataset_with_necessary_models

from .utils import generate_solr_params_for_user
from .views import UserFiles, user_files_csv

logger = logging.getLogger(__name__)


class UserFilesAPITests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = UserFiles.as_view()
        self.url_root = '/api/v2/files/'
        self.user = get_anonymous_user()

    def test_get(self):
        request = self.factory.get(self.url_root)
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual(sorted(response.data.keys()), [
            'attributes',
            'facet_field_counts',
            'nodes',
            'nodes_count'
        ])


class UserFilesUITests(StaticLiveServerTestCase):
    def setUp(self):
        # recommended solution to an auth_permission error, though doc says
        # we probably won't need to call it since django will call it
        # automatically when needed
        ContentType.objects.clear_cache()

    def test_ui(self):
        response = requests.get(
            urljoin(
                self.live_server_url,
                'files/'
            )
        )
        self.assertIn("All Files", response.content)

    @mock.patch('django.conf.settings.USER_FILES_COLUMNS', 'name,fake')
    def test_csv(self):
        response = requests.get(
            urljoin(
                self.live_server_url,
                'files_download'
            )
        )
        self.assertEqual(
            response.content,
            'url,name,fake\r\n'
        )


class UserFilesViewTests(TestCase):

    @mock.patch('django.conf.settings.USER_FILES_COLUMNS', 'filename,fake')
    def test_user_files_csv(self):
        request = RequestFactory().get('/fake-url')
        request.user = User.objects.create_user(
            'testuser', 'test@example.com', 'password')
        mock_doc = {
            NodeIndex.DOWNLOAD_URL:
                'fake-url',
            'filename_Characteristics' + NodeIndex.GENERIC_SUFFIX:
                'fake-filename',
            'organism_Factor_Value' + NodeIndex.GENERIC_SUFFIX:
                u'handles\u2013unicode'
            # Just want to exercise "_Characteristics" and "_Factor_Value":
            # Doesn't matter if the names are backwards.
        }
        with mock.patch(
            'user_files_manager.views._get_solr',
            return_value=json.dumps({
                'response': {
                    'docs': [mock_doc]
                }
            })
        ):
            response = user_files_csv(request)
            self.assertEqual(
                response.content,
                'url,filename,fake\r\n'
                'fake-url,fake-filename,\r\n'
            )


class UserFilesUtilsTests(TestCase):
    @override_settings(USER_FILES_FACETS="filetype,organism,technology,"
                                         "genotype,cell_type,antibody,"
                                         "experimenter")
    def setUp(self):
        self.user = User.objects.create_user(
            'testuser', 'test@example.com', 'password')
        self.dataset = create_dataset_with_necessary_models()
        self.dataset.set_owner(self.user)
        self.assay_uuid = Assay.objects.get(
            study=self.dataset.get_latest_study()
        ).uuid

    def test_generate_solr_params_for_user_returns_obj(self):
        query = generate_solr_params_for_user(QueryDict({}), self.user.id)
        self.assertItemsEqual(query.keys(), ['json', 'params'])

    def test_generate_solr_params_for_user_returns_params(self):
        query = generate_solr_params_for_user(QueryDict({}), self.user.id)
        self.assertItemsEqual(query.get('params'),
                              {
                                  'facet.limit': '-1',
                                  'fq': 'is_annotation:false',
                                  'rows': '1000',
                                  'start': '0',
                                  'wt': 'json'
                              })

    def test_generate_solr_params_for_user_returns_json_facet(self):
        query = generate_solr_params_for_user(QueryDict({}), self.user.id)
        self.assertListEqual(query.get('json').get('facet').keys(),
                             ['antibody_Characteristics_generic_s',
                              'technology_Characteristics_generic_s',
                              'cell_type_Characteristics_generic_s',
                              'organism_Characteristics_generic_s',
                              'antibody_Factor_Value_generic_s',
                              'genotype_Characteristics_generic_s',
                              'cell_type_Factor_Value_generic_s',
                              'filetype_Characteristics_generic_s',
                              'filetype_Factor_Value_generic_s',
                              'organism_Factor_Value_generic_s',
                              'experimenter_Factor_Value_generic_s',
                              'genotype_Factor_Value_generic_s',
                              'experimenter_Characteristics_generic_s',
                              'technology_Factor_Value_generic_s']
                             )

    def test_generate_solr_params_for_user_returns_json_fields(self):
        query = generate_solr_params_for_user(QueryDict({}), self.user.id)
        self.assertListEqual(query.get('json').get('fields'),
                             ['*_generic_s',
                              'name',
                              '*_uuid',
                              'uuid',
                              'type',
                              'django_id',
                              'REFINERY_DOWNLOAD_URL_s',
                              'filetype_Characteristics_generic_s',
                              'filetype_Factor_Value_generic_s',
                              'organism_Characteristics_generic_s',
                              'organism_Factor_Value_generic_s',
                              'technology_Characteristics_generic_s',
                              'technology_Factor_Value_generic_s',
                              'genotype_Characteristics_generic_s',
                              'genotype_Factor_Value_generic_s',
                              'cell_type_Characteristics_generic_s',
                              'cell_type_Factor_Value_generic_s',
                              'antibody_Characteristics_generic_s',
                              'antibody_Factor_Value_generic_s',
                              'experimenter_Characteristics_generic_s',
                              'experimenter_Factor_Value_generic_s']
                             )

    def test_generate_solr_params_for_user_returns_json_filter(self):
        query = generate_solr_params_for_user(QueryDict({}), self.user.id)
        self.assertListEqual(query.get('json').get('filter'),
                             ['assay_uuid:({})'.format(self.assay_uuid)]
                             )

    def test_generate_solr_params_for_user_returns_json_query(self):
        query = generate_solr_params_for_user(QueryDict({}), self.user.id)
        self.assertEqual(query.get('json').get('query'),
                         'django_ct:data_set_manager.node')
