"""
richtextpy.type

Copyright (c) 2016 Sachin Rekhi
"""

from delta import Delta

name = 'rich-text'
uri = 'http://github.com/sachinrekhi/richtextpy'

def create(initial_ops):
	return Delta(initial_ops)

def apply(snapshot_ops, delta_ops):
	snapshot = Delta(snapshot_ops)
	delta = Delta(delta_ops)
	return snapshot.compose(delta)

def compose(delta1_ops, delta2_ops):
	delta1 = Delta(delta1_ops)
	delta2 = Delta(delta2_ops)
	return delta1.compose(delta2)

def diff(delta1_ops, delta2_ops):
	delta1 = Delta(delta1_ops)
	delta2 = Delta(delta2_ops)
	return delta1.diff(delta2)

def transform(delta1_ops, delta2_ops, side):
	delta1 = Delta(delta1_ops)
	delta2 = Delta(delta2_ops)
	# fuzzer specs is in opposite order of delta interface
	return delta2.transform(delta1, True if side == 'left' else False)
