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

        myItem = DigdirRoadmapItem("test", 1234)
        myItem.set_closed_Info(timeline_items)

        self.assertEqual(myItem.closed_by, 'testdude2')

        self.assertEqual(myItem.closed_datetime.date(),
                         expected_closed_date.date())

    def test_set_closed_info_one_cloesedevent(self):

        expected_closed_date = datetime.datetime(2023, 10, 13)
        expected_actor = 'tester'
        timeline_item = self.__get_timeline_item(
            'ClosedEvent', expected_closed_date, expected_actor)

        timeline_items = {'nodes': [timeline_item]}

        myItem = DigdirRoadmapItem("test", 1234)
        myItem.set_closed_Info(timeline_items)

        self.assertEqual(myItem.closed_by, expected_actor)

        self.assertEqual(myItem.closed_datetime.date(),
                         expected_closed_date.date())

    def __get_timeline_item(self, EventType: str, createdAt: datetime, actor: str = None):
        timelineItem = {'__typename': EventType, 'createdAt': createdAt.strftime(
            '%Y-%m-%dT%H:%M:%SZ'), 'actor': {'login': actor}}

        return timelineItem


if __name__ == '__main__':
    unittest.main()
