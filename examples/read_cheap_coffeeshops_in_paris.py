from os.path import dirname, realpath, join

from bonobo import console_run
from bonobo.ext.opendatasoft import from_opendatasoft_api
from bonobo.io.file import FileWriter

OUTPUT_FILENAME = realpath(join(dirname(__file__), 'datasets/cheap_coffeeshops_in_paris.txt'))

console_run(
    from_opendatasoft_api(
        'liste-des-cafes-a-un-euro', netloc='opendata.paris.fr'
    ),
    lambda row: '{nom_du_cafe}, {adresse}, {arrondissement} Paris, France'.format(**row),
    FileWriter(OUTPUT_FILENAME),
)

print('Import done, read {} for results.'.format(OUTPUT_FILENAME))
