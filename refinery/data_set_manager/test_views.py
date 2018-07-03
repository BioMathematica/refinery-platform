import uuid

from django.conf import settings
from django.core.urlresolvers import reverse

import factory
from rest_framework import status, test

from core.views import NodeViewSet
from .models import Investigation, Node, Study


class NodeAPIv2AnonymousAccessTest(test.APITestCase):

    def setUp(self):
        self.node = NodeFactory()
        self.api_client = test.APIClient()

    def test_get_node_list(self):
        response = self.api_client.get(reverse('node-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_node_detail(self):
        url = reverse('node-detail', kwargs={'uuid': self.node.uuid})
        response = self.api_client.get(url, uuid=self.node.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_node(self):
        response = self.api_client.post(reverse('node-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_node(self):
        url = reverse('node-detail', kwargs={'uuid': self.node.uuid})
        response = self.api_client.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_node(self):
        url = reverse('node-detail', kwargs={'uuid': self.node.uuid})
        response = self.api_client.patch(url, {'file_uuid': str(uuid.uuid4())})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class NodeAPIv2GetDetailTest(test.APITestCase):

    def setUp(self):
        self.node = NodeFactory()
        request_factory = test.APIRequestFactory()
        view = NodeViewSet.as_view({'get': 'retrieve'})
        url = reverse('node-detail', kwargs={'uuid': self.node.uuid})
        request = request_factory.get(url)
        self.response = view(request, uuid=self.node.uuid)

    def test_get_children(self):
        self.assertEqual(self.response.data['child_nodes'], [])

    def test_get_parents(self):
        self.assertEqual(self.response.data['parent_nodes'], [])

    def test_get_aux_nodes(self):
        self.assertEqual(self.response.data['auxiliary_nodes'], [])

    def test_get_aux_node_task_states(self):
        self.assertIsNone(
            self.response.data['auxiliary_file_generation_task_state']
        )

    def test_get_file_extension(self):
        self.assertIsNone(self.response.data['file_extension'])

    def test_get_relative_file_store_item_url(self):
        self.assertIsNone(self.response.data['relative_file_store_item_url'])

    def test_get_uuid(self):
        self.assertEqual(self.response.data['uuid'], self.node.uuid)

    def test_node_api_v1_compatibility(self):
        # Assert that the meaningful response fields from Node api v1 are a
        # subset of the response from Node api v2
        # NOTE: Once we move away from a reliance on Node api v1 some of the
        # tests below can most likely be removed
        self.assertIn('analysis_uuid', self.response.data)
        self.assertIn('assay', self.response.data)
        self.assertIn('file_uuid', self.response.data)
        self.assertIn('name', self.response.data)
        self.assertIn('study', self.response.data)
        self.assertIn('subanalysis', self.response.data)
        self.assertIn('type', self.response.data)


class InvestigationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Investigation


class StudyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Study

    investigation = factory.SubFactory(InvestigationFactory)


class NodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Node

    study = factory.SubFactory(StudyFactory)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    username = 'guest'
    password = 'guest'
