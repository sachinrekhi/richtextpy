"""
richtextpy.type_utils

Copyright (c) 2016 Sachin Rekhi
"""

INFINITY = float('inf')
NULL_STRING = chr(0)

def is_list(value):
	return isinstance(value, list)

def is_string(value):
	return isinstance(value, basestring)

def is_dict(value):
	return isinstance(value, dict)

def is_number(value):
	return isinstance(value, (int, long, float))
