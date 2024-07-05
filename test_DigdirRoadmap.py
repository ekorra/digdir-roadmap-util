import unittest
import uuid
# from unittest.mock import Mock
from unittest.mock import patch
from DigdirRoadmap import *
from GithubGraphQL import get_github_projects
from DigdirRoadmap import DigdirRoadmapItem


class DigdirRoadmapTest(unittest.TestCase):

    # EXPECTED_STATE = 'CLOSED'
    # EXPECTED_ID = 'test_id'
    # EXPECTED_STATUS = 'levert'

    def setUp(self):
        self.expeded_state = 'CLOSED'
        self.expced_id = uuid.uuid4()
        self.expected_status = 'Levert'
        self.epxeded_progression = 100
        self.title_prefix = 'Title prefix'
        self.expected_other_label = 'program/nye-altinn'
        self.expected_start = '2023-06-01'
        self.expected_end = '2023-11-30'
        self.expected_estimerte_ukesverk = 10
        self.expected_product = 'test_issue_include'
        self.expected_product_label = f'product/{self.expected_product}'

        # extended itemInof
        self.expected_url = 'https://test.no'

    @patch('DigdirRoadmap.get_github_projects')
    @patch('DigdirRoadmap.DigdirRoadmapItem.get_issue_info')
    def test_get_digdir_roadmap(self, mock2, githubgrapql_patch):

        test_issue_include = self.getNode(123, 'product/test_issue_include')
        test_issue_exclude = self.getNode(456, 'product/test_issue_exclude')

        githubgrapql_patch.return_value = [
            test_issue_include, test_issue_exclude]

        roadmap_items = getDigdirRoadmap(
            'token', ['product/test_issue_include'])
        self.assertEqual(1, len(roadmap_items))
        self.assertEqual(123, roadmap_items[0].number)
        self.assertTrue(mock2.called)

    @patch('DigdirRoadmap.get_github_projects')
    @patch('DigdirRoadmap.DigdirRoadmapItem.get_issue_info')
    def test_integration_roadmapitem_properties_set(self, mock2, githubgrapql_patch):

        expcted_issue_number = 123
        expted_title = f'{self.title_prefix} {expcted_issue_number}'

        test_issue_include = self.getNode(
            expcted_issue_number, self.expected_product_label)

        githubgrapql_patch.return_value = [
            test_issue_include]

        roadmap_items = getDigdirRoadmap(
            'token', [self.expected_product_label])

        self.assertEqual(expcted_issue_number, roadmap_items[0].number)
        self.assertEqual(expted_title, roadmap_items[0].title)
        self.assertEqual(self.expected_status, roadmap_items[0].status)
        self.assertEqual(self.expeded_state, roadmap_items[0].state)
        self.assertEqual(
            self.expected_estimerte_ukesverk, roadmap_items[0].estimerte_ukesverk)
        self.assertEqual(self.expected_start, roadmap_items[0].start)
        self.assertEqual(self.expected_end, roadmap_items[0].end)
        self.assertIn(self.expected_product, roadmap_items[0].product)
        self.assertEqual(self.epxeded_progression, roadmap_items[0].progresjon)
        self.assertIn(self.expected_product_label, roadmap_items[0].labels)
        self.assertIn(self.expected_other_label, roadmap_items[0].labels)
        # self.assertEqual(self.expected_url, roadmap_items[0].url)

    def getNode(self, issue_number: int, product_label):
        node = {
            '__typename': 'ProjectV2Item',
            'id': 'PVTI_lADOAwyZKM4ANYNjzgIWpY4',
            'content': {
                'title': f'test tittel {issue_number}',
                'number': issue_number,
                'url': f'{self.expected_url}',
                'state': self.expeded_state
            },
            'fieldValues': {
                'nodes': [
                    {
                        '__typename': 'ProjectV2ItemFieldUserValue'
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldRepositoryValue'
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldLabelValue',
                        'field': {
                            'name': 'Labels'
                        },
                        'labels': {
                            'totalCount': 2,
                            'nodes': [
                                {
                                    'name': self.expected_other_label,
                                    'description': 'Del av programmet for moderniseringen av Altinn.',
                                    'url': 'https://github.com/digdir/roadmap/labels/program%2Fnye-altinn'
                                },
                                {
                                    'name': product_label,
                                    'description': 'Varsling og revarsling via epost eller SMS',
                                    'url': 'https://github.com/digdir/roadmap/labels/product%2Fvarsling'
                                }
                            ]
                        }
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldTextValue',
                        'field': {
                            'name': 'Title'
                        },
                        'text': f'{self.title_prefix} {issue_number}'
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldSingleSelectValue',
                        'field': {
                            'name': 'Status'
                        },
                        'name': self.expected_status
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldNumberValue',
                        'field': {
                            'name': 'Progresjon (%)'
                        },
                        'number': self.epxeded_progression
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldDateValue',
                        'field': {
                            'name': 'Start'
                        },
                        'date': self.expected_start
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldDateValue',
                        'field': {
                            'name': 'Sluttdato'
                        },
                        'date': self.expected_end
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldNumberValue',
                        'field': {
                            'name': 'Estimerte ukesverk'
                        },
                        'number': self.expected_estimerte_ukesverk
                    }
                ]
            }
        }
        return node


if __name__ == '__main__':
    unittest.main()
