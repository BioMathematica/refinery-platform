from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from core.views import NodeViewSet
from .models import Assay, Investigation, Node, Study


class NodeAPIv2AnonymousAccessTest(APITestCase):

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


class NodeAPIv2GetDetailTest(APITestCase):

    def setUp(self):
        investigation = Investigation.objects.create()
        study = Study.objects.create(investigation=investigation)
        assay = Assay.objects.create(study=study)
        self.node = Node.objects.create(assay=assay, study=study)

        factory = APIRequestFactory()
        view = NodeViewSet.as_view({'get': 'retrieve'})
        url = reverse('node-detail', kwargs={'uuid': self.node.uuid})
        request = factory.get(url)
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
