import unittest
# from unittest.mock import Mock
from unittest.mock import patch
from DigdirRoadmap import *
from GithubGraphQL import get_github_projects
from DigdirRoadmap import DigdirRoadmapItem


class DigdirRoadmapTest(unittest.TestCase):

    EXPECTED_STATE = 'CLOSED'
    EXPECTED_ID = 'test_id'
    EXPECTED_STATUS = 'levert'

    @patch('DigdirRoadmap.get_github_projects')
    @patch('DigdirRoadmap.DigdirRoadmapItem.get_issue_info')
    def test_get_digdir_roadmap(self, mock2, githubgrapql_patch):

        test_issue_include = self.getNode(123, 'test_issue_include')
        test_issue_exclude = self.getNode(456, 'test_issue_exclude')

        githubgrapql_patch.return_value = [
            test_issue_include, test_issue_exclude]

        roadmap_items = getDigdirRoadmap(
            'token', ['product/test_issue_include'])
        self.assertEqual(1, len(roadmap_items))
        self.assertEqual(123, roadmap_items[0].number)
        self.assertTrue(mock2.called)

    def getNode(self, issue_number: int, product_name):
        node = {
            '__typename': 'ProjectV2Item',
            'id': 'PVTI_lADOAwyZKM4ANYNjzgIWpY4',
            'content': {
                'title': f'test tittel {issue_number}',
                'number': issue_number,
                'url': f'https://test.com/{issue_number}',
                'state': 'CLOSED'
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
                                    'name': 'program/nye-altinn',
                                    'description': 'Del av programmet for moderniseringen av Altinn.',
                                    'url': 'https://github.com/digdir/roadmap/labels/program%2Fnye-altinn'
                                },
                                {
                                    'name': f'product/{product_name}',
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
                        'text': 'Varsling på epost'
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldSingleSelectValue',
                        'field': {
                            'name': 'Status'
                        },
                        'name': 'Levert'
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldNumberValue',
                        'field': {
                            'name': 'Progresjon (%)'
                        },
                        'number': 100
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldDateValue',
                        'field': {
                            'name': 'Start'
                        },
                        'date': '2023-06-01'
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldDateValue',
                        'field': {
                            'name': 'Sluttdato'
                        },
                        'date': '2023-11-30'
                    },
                    {
                        '__typename': 'ProjectV2ItemFieldNumberValue',
                        'field': {
                            'name': 'Estimerte ukesverk'
                        },
                        'number': 21
                    }
                ]
            }
        }
        return node


if __name__ == '__main__':
    unittest.main()
