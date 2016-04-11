"""
richtextpy.opiterator

Copyright (c) 2016 Sachin Rekhi
"""

from op import op_length
from type_utils import is_string, INFINITY


class OpIterator(object):
	def __init__(self, ops):	
		self.ops = ops
		self.index = 0
		self.offset = 0

	def has_next(self):
		return self.peek_length() < INFINITY

	def next(self, length=None):
		if length == None:
			length = INFINITY

		if self.index < len(self.ops):
			next_op = self.ops[self.index]
			offset = self.offset
			next_op_length = op_length(next_op)

			if (length >= next_op_length - offset):
				length = next_op_length - offset
				self.index += 1
				self.offset = 0
			else:
				self.offset += length

			return_op = dict()
			if 'attributes' in next_op:
				return_op['attributes'] = next_op['attributes']
			
			if 'delete' in next_op:
				return_op['delete'] = length
			elif 'retain' in next_op:
				return_op['retain'] = length
			elif 'insert' in next_op:
				if is_string(next_op['insert']):
					return_op['insert'] = next_op['insert'][offset:offset+length]
				else:
					return_op['insert'] = next_op['insert']

			return return_op
		else:
			return {'retain': INFINITY}

	def peek_length(self):
		if self.index < len(self.ops):
			# should never return 0 if our index is being managed correctly
			return op_length(self.ops[self.index]) - self.offset
		else:
			return INFINITY

	def peek_type(self):
		if self.index < len(self.ops):
			next_op = self.ops[self.index]
			if 'insert' in next_op:
				return 'insert'
			elif 'delete' in next_op:
				return 'delete'
			elif 'retain' in next_op:
				return 'retain'
		else:
			return 'retain'
