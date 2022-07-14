from os import path
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

def execfile(fname, globs, locs=None):
    locs = locs or globs
    exec(compile(open(fname).read(), fname, "exec"), globs, locs)

tolines = lambda c: list(filter(None, map(lambda s: s.strip(), c.split('\n'))))
try:
    with open(path.join(here, 'classifiers.txt'), encoding='utf-8') as f:
        classifiers = tolines(f.read())
except:
    classifiers = []

version_ns = {}
try:
    execfile(path.join(here, 'bonobo/_version.py'), version_ns)
except EnvironmentError:
    version = 'dev'
else:
    version = version_ns.get('__version__', 'dev')

with open('README.rst') as f:
    readme = f.read()


with open('LICENSE') as f:
    license = f.read()


def get_requirements():
    requirements = list()
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
    return requirements


def main():
    setup(name='bonobo',
        version=version,
        description=('Bonobo, a simple, modern and atomic extract-transform-load toolkit for python 3.10+.'),
        long_description=readme,
        include_package_data=True,
        classifiers=classifiers,
        python_requires='>=3.10.5',
        author="Civis Analytics Inc",
        author_email="asirifi@civisanalytics.com",
        packages=find_packages(exclude=['ez_setup', 'example', 'test']),
        license=license,
        install_requires=[
            'cached-property ~= 1.5.2', 'fs ~= 2.4.16', 'graphviz >= 0.20',
            'jinja2 ~= 3.1.2', 'mondrian ~= 0.8.1', 'packaging ~= 21.3',
            'psutil ~= 5.9.1', 'python-slugify ~= 6.1.2', 'requests ~= 2.28.1',
            'stevedore ~= 4.0.0', 'whistle ~= 1.0.1'
        ],
        entry_points={
            'bonobo.commands': [
                'convert = bonobo.commands.convert:ConvertCommand',
                'download = bonobo.commands.download:DownloadCommand',
                'examples = bonobo.commands.examples:ExamplesCommand',
                'init = bonobo.commands.init:InitCommand',
                'inspect = bonobo.commands.inspect:InspectCommand',
                'run = bonobo.commands.run:RunCommand',
                'version = bonobo.commands.version:VersionCommand'
            ],
            'console_scripts': ['bonobo = bonobo.commands:entrypoint']
        },
        url='https://www.bonobo-project.org/',
        download_url='https://github.com/python-bonobo/bonobo/tarball/{version}'.
        format(version=version),
    )


if __name__ == "__main__":
    main()
