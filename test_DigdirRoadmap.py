import unittest
import datetime
from DigdirRoadmap import DigdirRoadmapItem


class DigdirRoadmapTest(unittest.TestCase):

    def test_set_closed_info(self):

        timeline_items = eval(
            '''{'nodes':[
            {'__typename': 'LabeledEvent'},
            {'__typename': 'ClosedEvent', 'createdAt': '2023-10-12T09:07:21Z', 'actor': {'login': 'testdude1'}},
            {'__typename': 'ReopenedEvent'},
            {'__typename': 'ClosedEvent', 'createdAt': '2023-10-13T09:07:34Z', 'actor': {'login': 'testdude2'}},
            {'__typename': 'ClosedEvent', 'createdAt': '2023-10-11T09:07:34Z', 'actor': {'login': 'testdude3'}}
            ]}''')

        expected_closed_date = datetime.datetime(2023, 10, 13)

        myItem = DigdirRoadmapItem("test", 1234, '')
        myItem.__set_closed_Info(timeline_items)

        self.assertEqual(myItem.closed_by, 'testdude2')

        self.assertEqual(myItem.closed_datetime.date(),
                         expected_closed_date.date())


if __name__ == '__main__':
    unittest.main()
