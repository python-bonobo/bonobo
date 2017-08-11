import pkg_resources
from packaging.utils import canonicalize_name

bonobo_packages = {}
for p in pkg_resources.working_set:
    name = canonicalize_name(p.project_name)
    if name.startswith('bonobo'):
        bonobo_packages[name] = p
