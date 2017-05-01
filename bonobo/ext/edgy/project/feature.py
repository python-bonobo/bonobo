try:
    import edgy.project
except ImportError as e:
    import logging

    logging.exception('You must install edgy.project to use this.')

import os

from edgy.project.events import subscribe
from edgy.project.feature import Feature, SUPPORT_PRIORITY


class BonoboFeature(Feature):
    requires = {'python'}

    @subscribe('edgy.project.on_start', priority=SUPPORT_PRIORITY)
    def on_start(self, event):
        package_path = event.setup['name'].replace('.', os.sep)

        for file in ('example_graph'):
            self.render_file(os.path.join(package_path, file + '.py'), os.path.join('tornado', file + '.py.j2'))
