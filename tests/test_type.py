"""
richtextpy.tests.test_type

Copyright (c) 2016 Sachin Rekhi
"""

from unittest import TestCase
from richtextpy import type
from richtextpy import Delta


class TestType(TestCase):
	def test_name(self):
		self.assertEqual(type.name, 'rich-text')

	def test_uri(self):
		self.assertEqual(type.uri, 'http://github.com/sachinrekhi/richtextpy')

	def test_create(self):
		delta = type.create([{'delete': 3}])
		self.assertEqual(delta.get_ops(), [{'delete': 3}])

	def test_apply(self):
		delta = type.apply([{'insert': 'A'}], [{'insert': 'B'}])
		expected = Delta().insert('B').insert('A')
		self.assertEqual(delta, expected)

	def test_compose(self):
		delta = type.compose([{'insert': 'A'}], [{'insert': 'B'}])
		expected = Delta().insert('B').insert('A')
		self.assertEqual(delta, expected)

	def test_transform(self):
		delta = type.transform([{'retain': 1, 'attributes': {'bold': True, 'color': 'red'}}], [{'delete': 1}], 'left')
		expected = Delta()
		self.assertEqual(delta, expected)

	def test_diff(self):
		pass
