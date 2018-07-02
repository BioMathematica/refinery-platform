import json
import re

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from core.views import NodeViewSet
from .models import Assay, Investigation, Node, Study


class NodeAPIv2UnauthenticatedAccessTest(APITestCase):

    def setUp(self):
        investigation = Investigation.objects.create()
        study = Study.objects.create(investigation=investigation)
        self.node = Node.objects.create(study=study)
        self.factory = APIRequestFactory()

    def test_get_node_list(self):
        view = NodeViewSet.as_view({'get': 'list'})
        request = self.factory.get(reverse('node-list'))
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_node_detail(self):
        view = NodeViewSet.as_view({'get': 'retrieve'})
        url = reverse('node-detail', kwargs={'uuid': self.node.uuid})
        request = self.factory.get(url)
        response = view(request, uuid=self.node.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_node(self):
        view = NodeViewSet.as_view({'post': 'create'})
        request = self.factory.post(reverse('node-list'))
        response = view(request)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_node(self):
        view = NodeViewSet.as_view({'put': 'update'})
        url = reverse('node-detail', kwargs={'uuid': self.node.uuid})
        request = self.factory.put(url)
        response = view(request)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_node(self):
        view = NodeViewSet.as_view({'patch': 'partial_update'})
        url = reverse('node-detail', kwargs={'uuid': self.node.uuid})
        request = self.factory.patch(url)
        response = view(request)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class NodeApiV2Tests(APITestCase):

    def setUp(self):
        self.username = 'guest'
        self.password = 'guest'
        self.user = User.objects.create_user(self.username, '', self.password)

        self.investigation = Investigation.objects.create()
        self.study = Study.objects.create(investigation=self.investigation)
        self.assay = Assay.objects.create(study=self.study)
        self.node = Node.objects.create(assay=self.assay, study=self.study)

        self.node_json = json.dumps([{
            "uuid": "cfb31cca-4f58-4ef0-b1e2-4469c804bf73",
            "relative_file_store_item_url": None,
            "parent_nodes": [],
            "child_nodes": [
                "1d9ee2ee-d804-4458-93b9-b1fb9a08a2c8"
            ],
            "auxiliary_nodes": [],
            "is_auxiliary_node": False,
            "file_extension": None,
            "auxiliary_file_generation_task_state": None,
            "ready_for_igv_detail_view": None
        }])

        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.view = NodeViewSet.as_view({'get': 'list'})
        self.client.login(username=self.username, password=self.password)

        # Make a reusable request & response
        self.url_root = '/api/v2/node/'
        self.get_request = self.factory.get(self.url_root)
        self.get_response = self.view(self.get_request)

    def test_get_children(self):
        self.assertIsNotNone(self.get_response.data)
        self.assertEqual(self.get_response.data[0]['child_nodes'], [])

    def test_get_parents(self):
        self.assertIsNotNone(self.get_response.data)
        self.assertEqual(self.get_response.data[0]['parent_nodes'], [])

    def test_get_aux_nodes(self):
        self.assertIsNotNone(self.get_response.data)
        self.assertEqual(self.get_response.data[0]['auxiliary_nodes'], [])

    def test_get_aux_node_task_states(self):
        self.assertIsNotNone(self.get_response.data)
        self.assertEqual(
            self.get_response.data[0]['auxiliary_file_generation_task_state'],
            None
        )

    def test_get_file_extension(self):
        self.assertEqual(self.get_response.data[0]['file_extension'], None)

    def test_get_relative_file_store_item_url(self):
        self.assertEqual(
            self.get_response.data[0]['relative_file_store_item_url'],
            None
        )

    def test_get_basic_node(self):
        self.assertRegexpMatches(
            self.get_response.data[0]['uuid'],
            re.compile(
                '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            )
        )
        # Assert that the meaningful response fields from Node api v1 are a
        # subset of the response from Node api v2
        # NOTE: Once we move away from a reliance on Node api v1 some of the
        # tests below can most likely be removed
        self.assertTrue('analysis_uuid' in self.get_response.data[0])
        self.assertTrue('assay' in self.get_response.data[0])
        self.assertTrue('file_uuid' in self.get_response.data[0])
        self.assertTrue('name' in self.get_response.data[0])
        self.assertTrue('study' in self.get_response.data[0])
        self.assertTrue('subanalysis' in self.get_response.data[0])
        self.assertTrue('type' in self.get_response.data[0])
        self.assertTrue('uuid' in self.get_response.data[0])
