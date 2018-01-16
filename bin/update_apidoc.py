import os

from jinja2 import Environment, DictLoader

__path__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), '..'))

apidoc_root = 'docs/reference/api'


class Module:
    def __init__(self, name, title=None, *, automodule_options=None):

        self.name = name
        self.title = title or ' '.join(map(str.title, self.name.split('.')[1:]))
        self.automodule_options = automodule_options or list()

    def __repr__(self):
        return '<{} ({})>'.format(self.title, self.name)

    def asdict(self):
        return {
            'name': self.name,
            'title': self.title,
            'automodule_options': self.automodule_options,
        }

    def get_path(self):
        return os.path.join(__path__, apidoc_root, *self.name.split('.')) + '.rst'


modules = [
    Module('bonobo', title='Bonobo'),
    Module('bonobo.config'),
    Module('bonobo.constants', automodule_options=['no-members']),
    Module('bonobo.execution'),
    Module('bonobo.execution.contexts'),
    Module('bonobo.execution.events'),
    Module('bonobo.execution.strategies'),
    Module('bonobo.util'),
]



def underlined_filter(txt, chr):
    return txt + '\n' + chr * len(txt)


env = Environment(loader=DictLoader({
    'module': '''
{{ (':mod:`'~title~' <'~name~'>`') | underlined('=') }}

.. currentmodule:: {{ name }}

:Module: :mod:`{{ name }}`

.. automodule:: {{ name }}
{% for opt in automodule_options %}   :{{ opt }}:{{ "\n" }}{% endfor %}
    '''[1:-1] + '\n'}))
env.filters['underlined'] = underlined_filter

for module in modules:
    with open(module.get_path(), 'w+') as f:
        f.write(env.get_template('module').render(module.asdict()))
