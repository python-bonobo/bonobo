import os

from jinja2 import Environment, FileSystemLoader

from bonobo.commands import BaseCommand


class InitCommand(BaseCommand):
    TEMPLATES = {'default'}
    TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates')

    def add_arguments(self, parser):
        parser.add_argument('filename')
        parser.add_argument('--force', '-f', default=False, action='store_true')
        parser.add_argument('--template', '-t', choices=self.TEMPLATES, default='default')

    def handle(self, *, template, filename, force=False):
        template_name = template
        name, ext = os.path.splitext(filename)
        if ext != '.py':
            raise ValueError('Filenames should end with ".py".')

        loader = FileSystemLoader(self.TEMPLATES_PATH)
        env = Environment(loader=loader)
        template = env.get_template(template_name + '.py-tpl')

        if os.path.exists(filename) and not force:
            raise FileExistsError('Target filename already exists, use --force to override.')

        with open(filename, 'w+') as f:
            f.write(template.render(name=name))

        self.logger.info('Generated {} using template {!r}.'.format(filename, template_name))
