import os

from jinja2 import Environment, FileSystemLoader

from bonobo.commands import BaseCommand


class InitCommand(BaseCommand):
    TEMPLATES = {'bare', 'default'}
    TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates')

    def add_arguments(self, parser):
        parser.add_argument('filename')
        parser.add_argument('--force', '-f', default=False, action='store_true')

        target_group = parser.add_mutually_exclusive_group(required=False)
        target_group.add_argument('--template', '-t', choices=self.TEMPLATES, default='default')
        target_group.add_argument('--package', '-p', action='store_true', default=False)

    def create_file_from_template(self, *, template, filename):
        template_name = template
        name, ext = os.path.splitext(filename)
        if ext != '.py':
            raise ValueError('Filenames should end with ".py".')

        loader = FileSystemLoader(self.TEMPLATES_PATH)
        env = Environment(loader=loader)
        template = env.get_template(template_name + '.py-tpl')

        with open(filename, 'w+') as f:
            f.write(template.render(name=name))

        self.logger.info('Generated {} using template {!r}.'.format(filename, template_name))

    def create_package(self, *, filename):
        _, ext = os.path.splitext(filename)
        if ext != '':
            raise ValueError('Package names should not have an extension.')

        try:
            import medikit.commands
        except ImportError as exc:
            raise ImportError(
                'To initialize a package, you need to install medikit (pip install --upgrade medikit).'
            ) from exc

        package_name = os.path.basename(filename)
        medikit.commands.handle_init(
            os.path.join(os.getcwd(), filename, 'Projectfile'), name=package_name, requirements=['bonobo']
        )

        self.logger.info('Generated "{}" package with medikit.'.format(package_name))
        self.create_file_from_template(template='default', filename=os.path.join(filename, package_name, '__main__.py'))

        print('Your "{}" package has been created.'.format(package_name))
        print()
        print('Install it...')
        print()
        print('    pip install --editable {}'.format(filename))
        print()
        print('Then maybe run the example...')
        print()
        print('    python -m {}'.format(package_name))
        print()
        print('Enjoy!')

    def handle(self, *, template, filename, package=False, force=False):
        if os.path.exists(filename) and not force:
            raise FileExistsError('Target filename already exists, use --force to override.')

        if package:
            self.create_package(filename=filename)
        else:
            self.create_file_from_template(template=template, filename=filename)
