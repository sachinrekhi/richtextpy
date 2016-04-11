# richtextpy

An [operational transformation](https://en.wikipedia.org/wiki/Operational_transformation) library for rich text documents. It enables optimistic conflict-free collaborative editing scenarios (like [Google Docs](http://docs.google.com)) by providing a rich text document format as well as **compose()** and **transform()** methods for managing changes according to the [OT](https://en.wikipedia.org/wiki/Operational_transformation) algorithm.

This is a Python version of the [Javascript Rich Text](https://github.com/ottypes/rich-text) ottype.

To fully support collaborative editing, you'll also need a rich text editor that produces Delta objects on user changes as well as a server that implements the full [OT](https://en.wikipedia.org/wiki/Operational_transformation) collaboration protocol. See the references for details on the protocol and some libraries that provide these additional capabilities.

## Example

```python
from richtextpy import Delta

delta = Delta([
  {'insert': 'The quick '},
  {'insert': 'brown', 'attributes': {'color': 'brown'}},
  {'insert': ' fox'}
])

# keep the first 10 characters, delete the next 5, and insert a red 'red'
change = Delta().retain(10).delete(5).insert('red', {'color': 'red'})

"""
this produces:

[
	{'retain': 10},
	{'delete': 5},
	{'insert': 'red', 'attributes': {'color': 'red'}},
]
"""

composed = delta.compose(change)

"""
composed is now:

[
  {'insert': 'The quick '},
  {'insert': 'red', 'attributes': {'color': 'red'}},
  {'insert': ' fox'}
]
"""
```

## Installation
```python
python setup.py install
```

## Running Tests
```python
python setup.py test
```

## API Reference

Fully implements the original [ottypes/rich-text](https://github.com/ottypes/rich-text) interface. So feel free to use their [API reference](https://github.com/ottypes/rich-text).

## References
- [High-Latency, Low-Bandwidth Windowing in the Jupiter Collaboration System, 1995](http://lively-kernel.org/repository/webwerkstatt/projects/Collaboration/paper/Jupiter.pdf)
- [Google Wave Operational Transformation, 2010](http://wave-protocol.googlecode.com/hg/whitepapers/operational-transform/operational-transform.html)
- [Wikipedia: Operational Transformation](https://en.wikipedia.org/wiki/Operational_transformation)
- [ottypes/rich-text](https://github.com/ottypes/rich-text)
- [Quill Rich Text Editor](https://github.com/quilljs/quill/) - WYSIWYG Javascript Editor that products Delta objects on user changes
- [ShareJS](https://github.com/share/ShareJS) - NodeJS server that implements the OT collaboration protocol

## License

The MIT License (MIT)

Copyright (c) 2016 Sachin Rekhi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
