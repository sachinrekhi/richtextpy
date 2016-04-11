"""
richtextpy.tests.test_delta

Copyright (c) 2016 Sachin Rekhi
"""

from unittest import TestCase
from richtextpy import Delta


class TestDelta(TestCase):
	def test_constructor(self):
		delta = Delta()
		self.assertEqual(delta.get_ops(), [])

		delta = Delta([])
		self.assertEqual(delta.get_ops(), [])

		delta = Delta([{'delete': 3}])
		self.assertEqual(delta.get_ops(), [{'delete': 3}])

		existing_delta = Delta([{'delete': 3}])
		delta = Delta(existing_delta)
		self.assertEqual(delta.get_ops(), [{'delete': 3}])

		delta = Delta({'ops': [{'delete': 3}]})
		self.assertEqual(delta.get_ops(), [{'delete': 3}])

		delta = Delta('whoops')
		self.assertEqual(delta.get_ops(), [])

	def test_insert(self):
		delta = Delta()
		delta.insert('')
		self.assertEqual(delta.get_ops(), [])

		delta = Delta()
		delta.insert(' ')
		self.assertEqual(delta.get_ops(), [{'insert': ' '}])

		delta = Delta()
		delta.insert('hello')
		self.assertEqual(delta.get_ops(), [{'insert': 'hello'}])

		delta = Delta()
		delta.insert('hello', {})
		self.assertEqual(delta.get_ops(), [{'insert': 'hello'}])

		delta = Delta()
		delta.insert('hello', {'bold': True})
		self.assertEqual(delta.get_ops(), [{'insert': 'hello', 'attributes': {'bold': True}}])

		# old Quill format for embeds
		delta = Delta()
		delta.insert(1, {'image': 'https://octodex.github.com/images/labtocat.png'})
		self.assertEqual(delta.get_ops(), [{'insert': 1, 'attributes': {'image': 'https://octodex.github.com/images/labtocat.png'}}])

		# new Quill format for embeds
		delta = Delta()
		delta.insert({'image': 'https://octodex.github.com/images/labtocat.png'}, {'alt': 'Lab Octocat'})
		self.assertEqual(delta.get_ops(), [{'insert': {'image': 'https://octodex.github.com/images/labtocat.png'}, 'attributes': {'alt': 'Lab Octocat'}}])

	def test_delete(self):
		delta = Delta()
		delta.delete(0)
		self.assertEqual(delta.get_ops(), [])

		delta = Delta()
		delta.delete(-10)
		self.assertEqual(delta.get_ops(), [])

		delta = Delta()
		delta.delete('whoops')
		self.assertEqual(delta.get_ops(), [])

		delta = Delta()
		delta.delete(15)
		self.assertEqual(delta.get_ops(), [{'delete': 15}])

		delta = Delta()
		delta.delete(15L)
		self.assertEqual(delta.get_ops(), [{'delete': 15}])

	def test_retain(self):
		delta = Delta()
		delta.retain(0)
		self.assertEqual(delta.get_ops(), [])

		delta = Delta()
		delta.retain(-10)
		self.assertEqual(delta.get_ops(), [])

		delta = Delta()
		delta.retain('whoops')
		self.assertEqual(delta.get_ops(), [])

		delta = Delta()
		delta.retain(15)
		self.assertEqual(delta.get_ops(), [{'retain': 15}])

		delta = Delta()
		delta.retain(15, {})
		self.assertEqual(delta.get_ops(), [{'retain': 15}])

		delta = Delta()
		delta.retain(15, {'bold': True})
		self.assertEqual(delta.get_ops(), [{'retain': 15, 'attributes': {'bold': True}}])

	def test_simple_combines(self):
		delta = Delta().insert('hello ').insert('world')
		self.assertEqual(delta.get_ops(), [{'insert': 'hello world'}])

		delta = Delta().delete(10).delete(5)
		self.assertEqual(delta.get_ops(), [{'delete': 15}])

		delta = Delta().retain(10).retain(5)
		self.assertEqual(delta.get_ops(), [{'retain': 15}])

		delta = Delta().retain(10).retain(10).retain(10).delete(5).delete(5).delete(5)
		self.assertEqual(delta.get_ops(), [{'retain': 30}, {'delete': 15}])

	def test_cant_combine(self):
		# differing attributes
		delta = Delta().insert('hello ').insert('world', {'bold': True})
		self.assertEqual(delta.get_ops(), [{'insert': 'hello '}, {'insert': 'world', 'attributes': {'bold': True}}])

		delta = Delta().insert('world', {'bold': True}).insert('hello ')
		self.assertEqual(delta.get_ops(), [{'insert': 'world', 'attributes': {'bold': True}}, {'insert': 'hello '}])

		delta = Delta().retain(10).retain(5, {'bold': True})
		self.assertEqual(delta.get_ops(), [{'retain': 10}, {'retain': 5, 'attributes': {'bold': True}}])

		delta = Delta().retain(5, {'bold': True}).retain(10)
		self.assertEqual(delta.get_ops(), [{'retain': 5, 'attributes': {'bold': True}}, {'retain': 10}])

		# insert text + insert embed
		delta = Delta().insert('hello').insert({'image': 'https://octodex.github.com/images/labtocat.png'}, {'alt': 'Lab Octocat'})
		self.assertEqual(delta.get_ops(), [{'insert': 'hello'}, {'insert': {'image': 'https://octodex.github.com/images/labtocat.png'}, 'attributes': {'alt': 'Lab Octocat'}}])

	def test_reorder(self):
		delta = Delta().insert('hello').delete(3)
		self.assertEqual(delta.get_ops(), [{'insert': 'hello'}, {'delete': 3}])

		delta = Delta().delete(3).insert('hello')
		self.assertEqual(delta.get_ops(), [{'insert': 'hello'}, {'delete': 3}])

		delta = Delta().delete(3).delete(3).insert('hello')
		self.assertEqual(delta.get_ops(), [{'insert': 'hello'}, {'delete': 6}])

	def test_reorder_and_combine(self):
		delta = Delta().insert('hello').delete(3).insert(' world')
		self.assertEqual(delta.get_ops(), [{'insert': 'hello world'}, {'delete': 3}])

		delta = Delta().insert('hello').delete(3).insert(' world', {'bold': True})
		self.assertEqual(delta.get_ops(), [{'insert': 'hello'}, {'insert': ' world', 'attributes': {'bold': True}}, {'delete': 3}])

		delta = Delta().delete(3).delete(3).insert('hello').delete(3)
		self.assertEqual(delta.get_ops(), [{'insert': 'hello'}, {'delete': 9}])

	def test_length(self):
		delta = Delta().retain(10).retain(10).retain(10).delete(5).delete(5).delete(5)
		self.assertEqual(delta.length(), 45)

		delta = Delta().insert('hello').delete(3).insert(' world', {'bold': True})
		self.assertEqual(delta.length(), 14)

		delta = Delta().insert('hello').insert({'image': 'https://octodex.github.com/images/labtocat.png'}, {'alt': 'Lab Octocat'})
		self.assertEqual(delta.length(), 6)

	def test_chop(self):
		delta = Delta().retain(10).retain(10).retain(10).delete(5).delete(5).delete(5)
		self.assertEqual(delta.get_ops(), [{'retain': 30}, {'delete': 15}])

		delta = Delta().delete(5).delete(5).delete(5).retain(10).retain(10).retain(10)
		delta.chop()
		self.assertEqual(delta.get_ops(), [{'delete': 15}])

	def test_compose(self):
		# tests replicated from: https://github.com/ottypes/rich-text/blob/master/test/delta/compose.js

		# insert + insert
		a = Delta().insert('A')
		b = Delta().insert('B')
		expected = Delta().insert('B').insert('A')
		self.assertEqual(a.compose(b), expected)

		# insert + retain
		a = Delta().insert('A')
		b = Delta().retain(1, {'bold': True, 'color': 'red', 'font': None})
		expected = Delta().insert('A', {'bold': True, 'color': 'red'})
		self.assertEqual(a.compose(b), expected)

		# insert + delete
		a = Delta().insert('A')
		b = Delta().delete(1)
		expected = Delta()
		self.assertEqual(a.compose(b), expected)

		# delete + insert
		a = Delta().delete(1)
		b = Delta().insert('B')
		expected = Delta().insert('B').delete(1)
		self.assertEqual(a.compose(b), expected)

		# delete + retain
		a = Delta().delete(1)
		b = Delta().retain(1, {'bold': True, 'color': 'red'})
		expected = Delta().delete(1).retain(1, {'bold': True, 'color': 'red'})
		self.assertEqual(a.compose(b), expected)

		# delete + delete
		a = Delta().delete(1)
		b = Delta().delete(1)
		expected = Delta().delete(2)
		self.assertEqual(a.compose(b), expected)

		# retain + insert
		a = Delta().retain(1, {'color': 'blue'})
		b = Delta().insert('B')
		expected = Delta().insert('B').retain(1, {'color': 'blue'})
		self.assertEqual(a.compose(b), expected)

		# retain + retain
		a = Delta().retain(1, {'color': 'blue'})
		b = Delta().retain(1, {'bold': True, 'color': 'red', 'font': None})
		expected = Delta().retain(1, {'bold': True, 'color': 'red', 'font': None})
		self.assertEqual(a.compose(b), expected)

		# retain + delete
		a = Delta().retain(1, {'color': 'blue'})
		b = Delta().delete(1)
		expected = Delta().delete(1)
		self.assertEqual(a.compose(b), expected)

		# insert in middle of text
		a = Delta().insert('Hello')
		b = Delta().retain(3).insert('X')
		expected = Delta().insert('HelXlo')
		self.assertEqual(a.compose(b), expected)

		# insert and delete ordering
		a = Delta().insert('Hello')
		b = Delta().insert('Hello')
		insertFirst = Delta().retain(3).insert('X').delete(1)
		deleteFirst = Delta().retain(3).delete(1).insert('X')
		expected = Delta().insert('HelXo')
		self.assertEqual(a.compose(insertFirst), expected)
		self.assertEqual(b.compose(deleteFirst), expected)

		# insert embed
		a = Delta().insert(1, {'src': 'http://quilljs.com/image.png'})
		b = Delta().retain(1, {'alt': 'logo'})
		expected = Delta().insert(1, {'src': 'http://quilljs.com/image.png', 'alt': 'logo'})
		self.assertEqual(a.compose(b), expected)

		# delete entire text
		a = Delta().retain(4).insert('Hello')
		b = Delta().delete(9)
		expected = Delta().delete(4)
		self.assertEqual(a.compose(b), expected)

		# retain more than length of text
		a = Delta().insert('Hello')
		b = Delta().retain(10)
		expected = Delta().insert('Hello')
		self.assertEqual(a.compose(b), expected)

		# retain empty embed
		a = Delta().insert(1)
		b = Delta().retain(1)
		expected = Delta().insert(1)
		self.assertEqual(a.compose(b), expected)

		# remove all attributes
		a = Delta().insert('A', {'bold': True})
		b = Delta().retain(1, {'bold': None})
		expected = Delta().insert('A')
		self.assertEqual(a.compose(b), expected)

		# remove all embed attributes
		a = Delta().insert(2, {'bold': True})
		b = Delta().retain(1, {'bold': None})
		expected = Delta().insert(2)
		self.assertEqual(a.compose(b), expected)

		# immutability
		attr1 = {'bold': True}
		attr2 = {'bold': True}
		a1 = Delta().insert('Test', attr1)
		a2 = Delta().insert('Test', attr1)
		b1 = Delta().retain(1, {'color': 'red'}).delete(2)
		b2 = Delta().retain(1, {'color': 'red'}).delete(2)
		expected = Delta().insert('T', {'color': 'red', 'bold': True}).insert('t', attr1)
		self.assertEqual(a1.compose(b1), expected)
		self.assertEqual(a1, a2)
		self.assertEqual(b1, b2)
		self.assertEqual(attr1, attr2)

	def test_transform(self):
		# tests replicated from https://github.com/ottypes/rich-text/blob/master/test/delta/transform.js

		# insert + insert
		a1 = Delta().insert('A')
		b1 = Delta().insert('B')
		a2 = Delta(a1)
		b2 = Delta(b1)
		expected1 = Delta().retain(1).insert('B')
		expected2 = Delta().insert('B')
		self.assertEqual(a1.transform(b1, True), expected1)
		self.assertEqual(a2.transform(b2, False), expected2)

		# insert + retain
		a = Delta().insert('A')
		b = Delta().retain(1, {'bold': True, 'color': 'red'})
		expected = Delta().retain(1).retain(1, {'bold': True, 'color': 'red'})
		self.assertEqual(a.transform(b, True), expected)

		# insert + delete
		a = Delta().insert('A')
		b = Delta().delete(1)
		expected = Delta().retain(1).delete(1)
		self.assertEqual(a.transform(b, True), expected)

		# delete + insert
		a = Delta().delete(1)
		b = Delta().insert('B')
		expected = Delta().insert('B')
		self.assertEqual(a.transform(b, True), expected)

		# delete + retain
		a = Delta().delete(1)
		b = Delta().retain(1, {'bold': True, 'color': 'red'})
		expected = Delta()
		self.assertEqual(a.transform(b, True), expected)

		# delete + delete
		a = Delta().delete(1)
		b = Delta().delete(1)
		expected = Delta()
		self.assertEqual(a.transform(b, True), expected)

		# retain + insert
		a = Delta().retain(1, {'color': 'blue'})
		b = Delta().insert('B')
		expected = Delta().insert('B')
		self.assertEqual(a.transform(b, True), expected)

		# retain + retain
		a1 = Delta().retain(1, {'color': 'blue'})
		b1 = Delta().retain(1, {'bold': True, 'color': 'red'})
		a2 = Delta().retain(1, {'color': 'blue'})
		b2 = Delta().retain(1, {'bold': True, 'color': 'red'})
		expected1 = Delta().retain(1, {'bold': True})
		expected2 = Delta()
		self.assertEqual(a1.transform(b1, True), expected1)
		self.assertEqual(b2.transform(a2, True), expected2)

		# retain + retain without priority
		a1 = Delta().retain(1, {'color': 'blue'})
		b1 = Delta().retain(1, {'bold': True, 'color': 'red'})
		a2 = Delta().retain(1, {'color': 'blue' })
		b2 = Delta().retain(1, {'bold': True, 'color': 'red'})
		expected1 = Delta().retain(1, {'bold': True, 'color': 'red'})
		expected2 = Delta().retain(1, {'color': 'blue'})
		self.assertEqual(a1.transform(b1, False), expected1)
		self.assertEqual(b2.transform(a2, False), expected2)

		# retain + delete
		a = Delta().retain(1, {'color': 'blue'})
		b = Delta().delete(1)
		expected = Delta().delete(1)
		self.assertEqual(a.transform(b, True), expected)

		# alternating edits
		a1 = Delta().retain(2).insert('si').delete(5)
		b1 = Delta().retain(1).insert('e').delete(5).retain(1).insert('ow')
		a2 = Delta(a1)
		b2 = Delta(b1)
		expected1 = Delta().retain(1).insert('e').delete(1).retain(2).insert('ow')
		expected2 = Delta().retain(2).insert('si').delete(1)
		self.assertEqual(a1.transform(b1, False), expected1)
		self.assertEqual(b2.transform(a2, False), expected2)

		# conflicting appends
		a1 = Delta().retain(3).insert('aa')
		b1 = Delta().retain(3).insert('bb')
		a2 = Delta(a1)
		b2 = Delta(b1)
		expected1 = Delta().retain(5).insert('bb')
		expected2 = Delta().retain(3).insert('aa')
		self.assertEqual(a1.transform(b1, True), expected1)
		self.assertEqual(b2.transform(a2, False), expected2)

		# prepend + append
		a1 = Delta().insert('aa')
		b1 = Delta().retain(3).insert('bb')
		expected1 = Delta().retain(5).insert('bb')
		a2 = Delta(a1)
		b2 = Delta(b1)
		expected2 = Delta().insert('aa')
		self.assertEqual(a1.transform(b1, False), expected1)
		self.assertEqual(b2.transform(a2, False), expected2)

		# trailing deletes with differing lengths
		a1 = Delta().retain(2).delete(1)
		b1 = Delta().delete(3)
		expected1 = Delta().delete(2)
		a2 = Delta(a1)
		b2 = Delta(b1)
		expected2 = Delta()
		self.assertEqual(a1.transform(b1, False), expected1)
		self.assertEqual(b2.transform(a2, False), expected2)

		# immutability
		a1 = Delta().insert('A')
		a2 = Delta().insert('A')
		b1 = Delta().insert('B')
		b2 = Delta().insert('B')
		expected = Delta().retain(1).insert('B')
		self.assertEqual(a1.transform(b1, True), expected)
		self.assertEqual(a1, a2)
		self.assertEqual(b1, b2)

	def test_transform_position(self):
		# tests replicated from https://github.com/ottypes/rich-text/blob/master/test/delta/transform-position.js

		# insert before position
		delta = Delta().insert('A')
		self.assertEqual(delta.transform_position(2), 3)

		# insert after position
		delta = Delta().retain(2).insert('A')
		self.assertEqual(delta.transform_position(1), 1)

		# insert at position
		delta = Delta().retain(2).insert('A')
		self.assertEqual(delta.transform_position(2, True), 2)
		self.assertEqual(delta.transform_position(2, False), 3)

		# delete before position
		delta = Delta().delete(2)
		self.assertEqual(delta.transform_position(4), 2)

		# delete after position
		delta = Delta().retain(4).delete(2)
		self.assertEqual(delta.transform_position(2), 2)

		# delete across position
		delta = Delta().retain(1).delete(4)
		self.assertEqual(delta.transform_position(2), 1)

		# insert and delete before position
		delta = Delta().retain(2).insert('A').delete(2)
		self.assertEqual(delta.transform_position(4), 3)

		# insert before and delete across position
		delta = Delta().retain(2).insert('A').delete(4)
		self.assertEqual(delta.transform_position(4), 3)

		# delete before and delete across position
		delta = Delta().delete(1).retain(1).delete(4)
		self.assertEqual(delta.transform_position(4), 1)

	def test_slice(self):
		# tests replicated from https://github.com/ottypes/rich-text/blob/master/test/delta/helpers.js

		# start
		slice = Delta().retain(2).insert('A').slice(2)
		expected = Delta().insert('A')
		self.assertEqual(slice, expected)

		# start and end chop
		slice = Delta().insert('0123456789').slice(2, 7)
		expected = Delta().insert('23456')
		self.assertEqual(slice, expected)

		# start and end multiple chop
		slice = Delta().insert('0123', {'bold': True}).insert('4567').slice(3, 5)
		expected = Delta().insert('3', {'bold': True}).insert('4')
		self.assertEqual(slice, expected)

		# start and end
		slice = Delta().retain(2).insert('A', {'bold': True}).insert('B').slice(2, 3)
		expected = Delta().insert('A', {'bold': True })
		self.assertEqual(slice, expected)

		# no params
		delta = Delta().retain(2).insert('A', {'bold': True}).insert('B')
		slice = delta.slice()
		self.assertEqual(slice, delta)

		# split ops
		slice = Delta().insert('AB', {'bold': True}).insert('C').slice(1, 2)
		expected = Delta().insert('B', {'bold': True})
		self.assertEqual(slice, expected)

		# split ops multiple times
		slice = Delta().insert('ABC', {'bold': True}).insert('D').slice(1, 2)
		expected = Delta().insert('B', {'bold': True})
		self.assertEqual(slice, expected)

	def test_concat(self):
		# tests replicated from https://github.com/ottypes/rich-text/blob/master/test/delta/helpers.js

		# empty delta
		delta = Delta().insert('Test')
		concat = Delta()
		expected = Delta().insert('Test')
		self.assertEqual(delta.concat(concat), expected)

		# unmergeable
		delta = Delta().insert('Test')
		concat = Delta().insert('!', {'bold': True})
		expected = Delta().insert('Test').insert('!', {'bold': True})
		self.assertEqual(delta.concat(concat), expected)

		# mergeable
		delta = Delta().insert('Test', {'bold': True})
		concat = Delta().insert('!', {'bold': True}).insert('\n')
		expected = Delta().insert('Test!', {'bold': True }).insert('\n')
		self.assertEqual(delta.concat(concat), expected)

	def test_diff(self):
		# tests replicated from https://github.com/ottypes/rich-text/blob/master/test/delta/diff.js
		
		# insert
		a = Delta().insert('A')
		b = Delta().insert('AB')
		expected = Delta().retain(1).insert('B')
		self.assertEqual(a.diff(b), expected)

		# delete
		a = Delta().insert('AB')
		b = Delta().insert('A')
		expected = Delta().retain(1).delete(1)
		self.assertEqual(a.diff(b), expected)

		# retain
		a = Delta().insert('A')
		b = Delta().insert('A')
		expected = Delta()
		self.assertEqual(a.diff(b), expected)

		# format
		a = Delta().insert('A')
		b = Delta().insert('A', {'bold': True})
		expected = Delta().retain(1, {'bold': True})
		self.assertEqual(a.diff(b), expected)

		# embed integer match
		a = Delta().insert(1)
		b = Delta().insert(1)
		expected = Delta()
		self.assertEqual(a.diff(b), expected)

		# embed integer mismatch
		a = Delta().insert(1)
		b = Delta().insert(2)
		expected = Delta().delete(1).insert(2)
		self.assertEqual(a.diff(b), expected)

		# embed object match
		a = Delta().insert({'image': 'http://quilljs.com'})
		b = Delta().insert({'image': 'http://quilljs.com'})
		expected = Delta()
		self.assertEqual(a.diff(b), expected)

		# embed object mismatch
		a = Delta().insert({'image': 'http://quilljs.com', 'alt': 'Overwrite'})
		b = Delta().insert({'image': 'http://quilljs.com'})
		expected = Delta().insert({'image': 'http://quilljs.com'}).delete(1)
		self.assertEqual(a.diff(b), expected)

		# embed false positive
		a = Delta().insert(1)
		b = Delta().insert(chr(0)) # Placeholder char for embed in diff()
		expected = Delta().insert(chr(0)).delete(1)
		self.assertEqual(a.diff(b), expected)

		# error on non-documents
		a = Delta().insert('A')
		b = Delta().retain(1).insert('B')
		with self.assertRaises(Exception):
			a.diff(b)
		with self.assertRaises(Exception):
			b.diff(a)

		# inconvenient indexes
		a = Delta().insert('12', {'bold': True}).insert('34', {'italic': True})
		b = Delta().insert('123', {'color': 'red'})
		expected = Delta().retain(2, {'bold': None, 'color': 'red'}).retain(1, {'italic': None, 'color': 'red'}).delete(1)
		self.assertEqual(a.diff(b), expected)

		# combination
		a = Delta().insert('Bad', {'color': 'red'}).insert('cat', {'color': 'blue'})
		b = Delta().insert('Good', {'bold': True}).insert('dog', {'italic': True})
		expected = Delta().insert('Good', {'bold': True}).delete(2).retain(1, {'italic': True, 'color': None}).delete(3).insert('og', {'italic': True})
		self.assertEqual(a.diff(b), expected)

		# same document
		a = Delta().insert('A').insert('B', {'bold': True})
		expected = Delta()
		self.assertEqual(a.diff(a), expected)

		# immutability
		attr1 = {'color': 'red'}
		attr2 = {'color': 'red'}
		a1 = Delta().insert('A', attr1)
		a2 = Delta().insert('A', attr1)
		b1 = Delta().insert('A', {'bold': True}).insert('B')
		b2 = Delta().insert('A', {'bold': True}).insert('B')
		expected = Delta().retain(1, {'bold': True, 'color': None}).insert('B')
		self.assertEqual(a1.diff(b1), expected)
		self.assertEqual(a1, a2)
		self.assertEqual(b2, b2)
		self.assertEqual(attr1, attr2)
