from bonobo.commands import BaseCommand

all_examples = (
    'clock',
    'datasets',
    'environ',
    'files.csv_handlers',
    'files.json_handlers',
    'files.pickle_handlers',
    'files.text_handlers',
    'types',
)


class ExamplesCommand(BaseCommand):
    def handle(self):
        print('You can run the following examples:')
        print()
        for example in all_examples:
            print('  $ python -m bonobo.examples.{}'.format(example))
        print()

    def add_arguments(self, parser):
        pass
