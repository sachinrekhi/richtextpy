# richtextpy

An operational transformation library for rich text documents. This library is suitable for [Operational Transformation](https://en.wikipedia.org/wiki/Operational_transformation) and defines several functions ([`compose`](#compose), [`transform`](#transform)) to support this use case.

This is a Python-version of the original [Javascript Rich-Text ottype](https://github.com/ottypes/rich-text).

## Quick Example

```python
from richtextpy import Delta

delta = Delta([
  {'insert': 'Gandalf', 'attributes': {'bold': True}},
  {'insert': ' the '},
  {'insert': 'Grey', 'attributes': {'color': '#ccc'}}
])

// Keep the first 12 characters, delete the next 4, and insert a white 'White'
death = Delta().retain(12).insert('White', {'color': '#fff'}).delete(4)

// this produces:
//   [
//     {'retain': 12 },
//     {'insert': 'White', 'attributes': {'color': '#fff'}},
//     {'delete': 4 }
//   ]

delta.compose(death)
// delta is now:
//	 [
//     {'insert': 'Gandalf ', 'attributes': {'bold': True}},
//     {'insert': ' the '},
//     {'insert': 'White', 'attributes': {'color': '#fff'}}
//   ]
```