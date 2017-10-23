from unittest import TestCase

import pytest

from bonobo import Bag
from bonobo.nodes.factory import Factory
from bonobo.util.testing import BufferingNodeExecutionContext


@pytest.mark.filterwarnings('ignore:Factory')
class FactoryTypeTest(TestCase):
    def execute_node(self, node, *rows):
        with BufferingNodeExecutionContext(node) as context:
            context.write_sync(*map(Bag, rows))
        return context.get_buffer()

    def test_args_as_str(self):
        f = Factory()
        f[0].as_str().upper()

        output = self.execute_node(f, 'foo', 'bar', 'baz')

        assert len(output) == 3
        assert output[0] == 'FOO'
        assert output[1] == 'BAR'
        assert output[2] == 'BAZ'

    def test_kwargs_as_str(self):
        f = Factory()
        f['foo'].as_str().upper()

        output = self.execute_node(f, {'foo': 'bar'}, {'foo': 'baz'})
        assert len(output) == 2
        assert output[0] == {'foo': 'BAR'}
        assert output[1] == {'foo': 'BAZ'}


"""
draft below.

if __name__ == '__main__':
    f = Factory()

    f[0].dict().map_keys({'foo': 'F00'})

    print('operations:', f.operations)
    print(f({'foo': 'bisou'}, foo='blah'))
    
specs:

- rename keys of an input dict (in args, or kwargs) using a translation map.


f = Factory()

f[0]
f['xxx'] = 
    
f[0].dict().get('foo.bar').move_to('foo.baz').apply(str.upper)
f[0].get('foo.*').items().map(str.lower)

f['foo'].keys_map({
    'a': 'b'
})

"""
