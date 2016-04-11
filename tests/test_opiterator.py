"""
richtextpy.tests.test_opiterator

Copyright (c) 2016 Sachin Rekhi
"""

from unittest import TestCase
from richtextpy import Delta
from richtextpy.opiterator import OpIterator


class TestOpIterator(TestCase):
	def test_iterator(self):
		delta = Delta().retain(20).insert('hello').delete(15).retain(3).insert({'image': 'https://octodex.github.com/images/labtocat.png'})

		iterator = OpIterator(delta.get_ops())

		self.assertEqual(iterator.peek_length(), 20)
		self.assertEqual(iterator.peek_type(), 'retain')
		self.assertEqual(iterator.next(), {'retain': 20})
		self.assertEqual(iterator.next(3), {'insert': 'hel'})
		self.assertEqual(iterator.peek_length(), 2)
		self.assertEqual(iterator.next(), {'insert': 'lo'})
		self.assertEqual(iterator.next(), {'delete': 15})
		self.assertEqual(iterator.has_next(), True)
		self.assertEqual(iterator.next(4), {'retain': 3})
		self.assertEqual(iterator.peek_length(), 1)
		self.assertEqual(iterator.next(5), {'insert': {'image': 'https://octodex.github.com/images/labtocat.png'}})
