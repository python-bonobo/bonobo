import inspect
import os

from jinja2 import DictLoader, Environment

__path__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), ".."))

apidoc_root = "docs/reference/api"


class Module:
    def __init__(self, name, title=None, *, automodule_options=None, append=None):
        self.append = append
        self.name = name
        self.title = title or " ".join(map(str.title, self.name.split(".")[1:]))
        self.automodule_options = automodule_options or list()

    def __repr__(self):
        return "<{} ({})>".format(self.title, self.name)

    def asdict(self):
        return {
            "append": self.append,
            "automodule": True,
            "automodule_options": self.automodule_options,
            "name": self.name,
            "title": self.title,
        }

    def get_path(self):
        return os.path.join(__path__, apidoc_root, *self.name.split(".")) + ".rst"


bonobo = __import__("bonobo")
assert bonobo.__version__

prefixes = {
    "bonobo.nodes": None,
    "bonobo._api": "bonobo",
    "bonobo.structs.graphs": None,
    "bonobo.execution.strategies": "bonobo",
    "bonobo.registry": "bonobo",
    "bonobo.util.environ": "bonobo",
}
api_objects = {}

display_order = [("bonobo.structs.graphs", "Graphs"), ("bonobo.nodes", "Nodes"), ("bonobo", "Other top-level APIs")]

for name in sorted(dir(bonobo)):
    # ignore attributes starting by underscores
    if name.startswith("_"):
        continue
    attr = getattr(bonobo, name)
    if inspect.ismodule(attr):
        continue

    assert name in bonobo.__all__

    o = getattr(bonobo, name)
    modname = inspect.getmodule(o).__name__
    family = None
    family_override = None

    for prefix, target in prefixes.items():
        if modname == prefix or modname.startswith(prefix + "."):
            family = target or prefix
            display_name = ".".join([family, name])
            break

    if family is None:
        raise Exception("Could not find family for {}".format(name))

    api_objects.setdefault(family, [])
    api_objects[family].append((name, o))

api_content = []
current_family = None
for family, title in display_order:
    if family != current_family:
        if current_family is not None:
            api_content.append("")
            api_content.append("")
        api_content.append(title)
        api_content.append(":" * len(title))
        api_content.append("")
        current_family = family

    for api_object in sorted(api_objects[family]):
        object_type = "func" if inspect.isfunction(api_object[1]) else "class"
        api_content.append("* :{}:`{}.{}` ".format(object_type, family, api_object[0]))

    if family == "bonobo":
        for api_object in sorted(api_objects[family]):
            object_type = "function" if inspect.isfunction(api_object[1]) else "class"
            api_content.append("")
            api_content.append("")
            api_content.append(api_object[0])
            api_content.append("-" * len(api_object[0]))
            api_content.append("")
            api_content.append(".. auto{}:: {}.{}".format(object_type, family, api_object[0]))


print("\n".join(api_content))

modules = [
    Module("bonobo", title="Bonobo", automodule_options=["no-members"], append="\n".join(api_content)),
    Module("bonobo.config"),
    Module("bonobo.constants", automodule_options=["no-members"]),
    Module("bonobo.execution"),
    Module("bonobo.execution.contexts"),
    Module("bonobo.execution.events"),
    Module("bonobo.execution.strategies"),
    Module("bonobo.nodes"),
    Module("bonobo.structs.graphs", title="Graphs"),
    Module("bonobo.util"),
]


def underlined_filter(txt, chr):
    return txt + "\n" + chr * len(txt)


env = Environment(
    loader=DictLoader(
        {
            "module": """
{{ (':mod:`'~title~' <'~name~'>`') | underlined('=') }}

.. currentmodule:: {{ name }}

:Module: :mod:`{{ name }}`

{% if automodule %}
.. automodule:: {{ name }}
{% for opt in automodule_options %}   :{{ opt }}:{{ "\n" }}{% endfor %}
{% endif %}
{% if append %}
{{ append }}
{% endif %}
    """[
                1:-1
            ]
            + "\n"
        }
    )
)
env.filters["underlined"] = underlined_filter

for module in modules:
    with open(module.get_path(), "w+") as f:
        f.write(env.get_template("module").render(module.asdict()))
