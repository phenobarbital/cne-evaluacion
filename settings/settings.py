"""
Settings Configuration for CNE

Basic Configuration.
"""
import sys
from navconfig.logging import logging
from navconfig import config, BASE_DIR


## disable some loggers.
logging.getLogger('visions.backends').setLevel(logging.CRITICAL)
logging.getLogger('matplotlib').setLevel(logging.CRITICAL)

# configuracion de directorios:
DIRECTORIO_ACTAS = config.get('DIRECTORIO_ACTAS')
DIRECTORIO_ACTAS_PROCESADAS = config.get('DIRECTORIO_ACTAS_PROCESADAS')

EXTENSION_ACTAS = config.get('EXTENSION_ACTAS')
EXTENSION_ACTAS = EXTENSION_ACTAS.split(',')
