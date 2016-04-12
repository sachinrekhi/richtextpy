"""
richtextpy.delta

Copyright (c) 2016 Sachin Rekhi
"""

from copy import deepcopy
from diff_match_patch import diff_match_patch
from type_utils import is_list, is_string, is_dict, is_number, INFINITY
from op import op_length, op_insert_string, attr_compose, attr_transform, attr_diff
from opiterator import OpIterator


class Delta(object):
	def __init__(self, ops=None):
		# assume we are given well formed ops as a Delta instance, list of op dicts, or dict with ops key
		if isinstance(ops, Delta):
			self.ops = ops.ops
		elif is_list(ops):
			self.ops = ops
		elif is_dict(ops) and is_list(ops.get('ops')):
			self.ops = ops['ops']
		else:
			self.ops = []

	def __eq__(self, other):
		if type(other) is type(self):
			return self.ops == other.ops
		else:
			return False

	def __ne__(self, other):
		return not self.__eq__(other)

	def get_ops(self):
		return deepcopy(self.ops)

	def insert(self, value, attributes=None):
		if is_string(value) and (len(value) == 0):
			return self

		insert_op = {'insert': value}

		if is_dict(attributes) and len(attributes) > 0:
			insert_op['attributes'] = attributes

		return self.push(insert_op)

	def delete(self, length):
		if not is_number(length) or length <= 0:
			return self

		return self.push({'delete': length})

	def retain(self, length, attributes=None):
		if not is_number(length) or length <= 0:
			return self

		retain_op = {'retain': length}

		if is_dict(attributes) and len(attributes) > 0:
			retain_op['attributes'] = attributes

		return self.push(retain_op)

	def push(self, op):
		# when adding an operation to this delta, ensure always end up with most compact possible representation
		# this requires combining same operation types when possible
		# and re-ordering same-index inserts and deletes to ensure canonical order

		new_op = deepcopy(op)

		# if no existing ops, simply add new_op
		if len(self.ops) == 0:
			self.ops.append(new_op)
			return self
		
		new_index = len(self.ops)
		last_op = self.ops[-1]

		# if new and last ops are both deletes, then combine
		if ('delete' in new_op) and ('delete' in last_op):
			self.ops[new_index - 1] = {'delete': last_op['delete'] + new_op['delete']}
			return self

		# since it does not matter if we insert before or after deleting at the same index, always prefer to insert first
		# so swap if this situation arises
		if ('delete' in last_op) and ('insert' in new_op):
			new_index -= 1
			if new_index - 1 < 0:
				self.ops.insert(0, new_op)
				return self
			last_op = self.ops[new_index - 1]

		# if attributes match, can combine insert or retain ops
		if new_op.get('attributes') == last_op.get('attributes'):
			if is_string(new_op.get('insert')) and is_string(last_op.get('insert')):
				self.ops[new_index - 1] = {'insert': last_op['insert'] + new_op['insert']}
				if new_op.get('attributes'):
					self.ops[new_index - 1]['attributes'] = new_op['attributes']
				return self
			elif ('retain' in new_op) and ('retain' in last_op):
				self.ops[new_index - 1] = {'retain': last_op['retain'] + new_op['retain']}
				if new_op.get('attributes'):
					self.ops[new_index - 1]['attributes'] = new_op['attributes']
				return self

		self.ops.insert(new_index, new_op)
		return self

	def length(self):
		return sum([op_length(op) for op in self.ops])

	def chop(self):
		if (len(self.ops) > 0) and ('retain' in self.ops[-1]) and ('attributes' not in self.ops[-1]):
			self.ops.pop()
		return self

	def compose(self, other):
		self_iter = OpIterator(self.ops)
		other_iter = OpIterator(other.ops)
		delta = Delta()

		while self_iter.has_next() or other_iter.has_next():
			if other_iter.peek_type() == 'insert':
				delta.push(other_iter.next())
			elif self_iter.peek_type() == 'delete':
				delta.push(self_iter.next())
			else:
				length = min(self_iter.peek_length(), other_iter.peek_length())
				self_op = self_iter.next(length)
				other_op = other_iter.next(length)
				if 'retain' in other_op:
					new_op = dict()
					if 'retain' in self_op:
						new_op['retain'] = length
					else:
						new_op['insert'] = self_op['insert']

					# preserve nulls in attributes when composing with a retain, otherwise remove it for inserts
					attributes = attr_compose(self_op.get('attributes'), other_op.get('attributes'), True if ('retain' in self_op) else False)
					if attributes != None:
						new_op['attributes'] = attributes
					delta.push(new_op)
				elif ('delete' in other_op) and ('retain' in self_op):
					delta.push(other_op)
		
		return delta.chop()

	def transform(self, other, priority=True):
		self_iter = OpIterator(self.ops)
		other_iter = OpIterator(other.ops)
		delta = Delta()

		while self_iter.has_next() or other_iter.has_next():
			if self_iter.peek_type() == 'insert' and (priority or other_iter.peek_type() != 'insert'):
				delta.retain(op_length(self_iter.next()))
			elif other_iter.peek_type() == 'insert':
				delta.push(other_iter.next())
			else:
				length = min(self_iter.peek_length(), other_iter.peek_length())
				self_op = self_iter.next(length)
				other_op = other_iter.next(length)

				if 'delete' in self_op:
					continue
				elif 'delete' in other_op:
					delta.push(other_op)
				else:
					delta.retain(length, attr_transform(self_op.get('attributes'), other_op.get('attributes'), priority))

		return delta.chop()

	def transform_position(self, index, priority=True):
		self_iter = OpIterator(self.ops)
		offset = 0

		while self_iter.has_next() and (offset <= index):
			length = self_iter.peek_length()
			next_type = self_iter.peek_type()
			self_iter.next()
			if (next_type == 'delete'):
				index -= min(length, index - offset)
				continue
			elif next_type == 'insert' and ((offset < index) or not priority):
				index += length
			offset += length

		return index

	def slice(self, start=0, end=None):
		if end == None:
			end = INFINITY
		
		delta = Delta()
		self_iter = OpIterator(self.ops)
		index = 0

		while (index < end) and self_iter.has_next():
			if (index < start):
				next_op = self_iter.next(start - index)
			else:
				next_op = self_iter.next(end - index)
				delta.push(next_op)
			index += op_length(next_op)

		return delta

	def concat(self, other):
		delta = self.slice()
		if len(other.ops) > 0:
			delta.push(other.ops[0])
			delta.ops.extend(other.ops[1:])
		return delta

	def diff(self, other):
		delta = Delta()

		# first check if no diff
		if (self.ops == other.ops):
			return delta

		self_string = ''.join([op_insert_string(op) for op in self.ops])
		other_string = ''.join([op_insert_string(op) for op in other.ops])

		self_iter = OpIterator(self.ops)
		other_iter = OpIterator(other.ops)
		changes = diff_match_patch().diff_main(self_string, other_string)
		for change in changes:
			change_type = change[0]
			length = len(change[1])

			while length > 0:
				op_length = 0

				if change_type == diff_match_patch.DIFF_INSERT:
					op_length = min(other_iter.peek_length(), length)
					delta.push(other_iter.next(op_length))
				elif change_type == diff_match_patch.DIFF_DELETE:
					op_length = min(length, self_iter.peek_length())
					self_iter.next(op_length)
					delta.delete(op_length)
				elif change_type == diff_match_patch.DIFF_EQUAL:
					op_length = min(self_iter.peek_length(), other_iter.peek_length(), length)
					self_op = self_iter.next(op_length)
					other_op = other_iter.next(op_length)
					if self_op['insert'] == other_op['insert']:
						delta.retain(op_length, attr_diff(self_op.get('attributes'), other_op.get('attributes')))
					else:
						delta.push(other_op).delete(op_length)

				length -= op_length

		return delta.chop()
