import unittest
import datetime
from DigdirRoadmap import DigdirRoadmapItem


class DigdirRoadmapItemTest(unittest.TestCase):

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

    def test_set_closed_info_timeline_item_none(self):

        expected_closed_date = None
        expected_actor = None
        timeline_item = None

        timeline_items = {'nodes': [timeline_item]}

        myItem = DigdirRoadmapItem("test", 1234)
        myItem.set_closed_Info(timeline_items)

        self.assertEqual(myItem.closed_by, expected_actor)

        self.assertEqual(myItem.closed_datetime,
                         expected_closed_date)

    def test_set_closed_info_multiple_nodes(self):

        expected_closed_date = datetime.datetime(2023, 10, 13)
        expected_actor = 'tester'
        timeline_item = self.__get_timeline_item(
            'ClosedEvent', expected_closed_date, expected_actor)
        timeline_item_none = None
        timeline_item_older1 = self.__get_timeline_item(
            'ClosedEvent', datetime.datetime(2023, 10, 12), 'tester_x')
        timeline_item_older2 = self.__get_timeline_item(
            'ClosedEvent', datetime.datetime(2023, 10, 11), 'tester_x')

        timeline_items = {'nodes': [
            timeline_item_older1, timeline_item_none, timeline_item, timeline_item_older2]}

        myItem = DigdirRoadmapItem("test", 1234)
        myItem.set_closed_Info(timeline_items)

        self.assertEqual(myItem.closed_by, expected_actor)

        self.assertEqual(myItem.closed_datetime.date(),
                         expected_closed_date.date())

    def __get_timeline_item(self, EventType, createdAt: datetime, actor: str = None):
        timelineItem = {'__typename': EventType, 'createdAt': createdAt.strftime(
            '%Y-%m-%dT%H:%M:%SZ'), 'actor': {'login': actor}}

        return timelineItem


if __name__ == '__main__':
    unittest.main()
